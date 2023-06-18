import stanza
from transformers import pipeline
import emoji
import pandas as pd

from Utilities.utils import prepare_sentence

def load_tagger_models():
    ner_model = pipeline(task='ner', model='saattrupdan/nbailab-base-ner-scandi', aggregation_strategy='first')
    pos_model = stanza.Pipeline("da", processors='tokenize,pos', use_gpu=True, cache_directory='./cache', tokenize_pretokenized=True, n_process=4)
    return ner_model, pos_model

def find_emoji_indexes(text):
    emoji_indexes = []
    for index, char in enumerate(text):
        if emoji.is_emoji(char):
            emoji_indexes.append(index)
    return emoji_indexes

def strip_emojis(text):
    cleaned_text = ""
    for char in text:
        if not emoji.is_emoji(char):
            cleaned_text += char
    return cleaned_text

class Tagger():
    def __init__(self) -> None:
        self.ner_tagger, self.pos_tagger = load_tagger_models()

    def turn_features_to_dicts(self, features):
        feature_dicts = []
        current_tense = None
        for feature in features:
            if feature is None:
                feature_dicts.append({})
                continue
            feature_dict = {}
            current_features = feature.split("|")
            for current_feature in current_features:
                key, value = current_feature.split("=")
                if key == "Tense" and current_tense is None:
                    current_tense = value
                feature_dict[key] = value
            if "Tense" not in feature_dict and "VerbForm" in feature_dict and key is not None:
                feature_dict["Tense"] = "Pres" if current_tense is None else current_tense
            feature_dicts.append(feature_dict)
        return feature_dicts

    def get_pos_tags(self, sentence):
        words = prepare_sentence(sentence, lowercase=False, clean=True)
        sentence = " ".join(words)
        doc = self.pos_tagger(sentence)
        features = [word.feats if word.feats else None for sentence in doc.sentences for word in sentence.words]
        feature_dicts = self.turn_features_to_dicts(features)
        results = [[word.upos, [word.start_char, word.end_char], feature_dicts[i]] for sentence in doc.sentences for i, word in enumerate(sentence.words)]
        return results
    
    def move_ner_tags_by_emoji(self, namedEntities, sentence):
        emoji_indexes = find_emoji_indexes(sentence)
        for namedEntity in namedEntities:
            for emoji_index in emoji_indexes:
                if emoji_index < namedEntity[1][0]:
                    namedEntity[1][0] += 1
                    namedEntity[1][1] += 1
                elif emoji_index < namedEntity[1][1]:
                    namedEntity[1][1] += 1
        return namedEntities
    
    def get_ner_tags(self, sentence):
        emoji_free_sentence = strip_emojis(sentence)
        result = self.ner_tagger.predict(emoji_free_sentence)
        namedEntities = [[ent["word"], [ent["start"], ent["end"]]] for ent in result]
        no_misc_entities = [namedEntity for i, namedEntity in enumerate(namedEntities) if result[i]["entity_group"] != "MISC"]
        emoji_corrected_entities = self.move_ner_tags_by_emoji(no_misc_entities, sentence)
        ner_word_indexes = self.ner_character_index_to_word_index(sentence, emoji_corrected_entities)
        return ner_word_indexes

    def ner_character_index_to_word_index(self, sentence, ner_tags):
        words_indexes = []
        words = sentence.split(" ")
        for (word, indexes) in ner_tags:
            start_index, end_index = 0, 0
            for i, word in enumerate(words):
                if start_index >= indexes[0]:
                    end_index += start_index
                    break
                start_index += len(word) + 1
            for word in words[i:]:
                words_indexes.append(i)
                end_index += len(word)
                if end_index >= indexes[1]:
                    break
                i += 1
                end_index += 1
        return words_indexes
                
    # run this function to get all tags
    def get_tags(self, sentence):
        pos = self.get_pos_tags(sentence)
        ner = self.get_ner_tags(sentence)
        return pos, ner