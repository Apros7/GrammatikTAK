import stanza
from danlp.models import load_bert_ner_model
from Utilities.utils import prepare_sentence

def load_models():
    ner_model = load_bert_ner_model()
    pos_model = stanza.Pipeline("da", processors='tokenize,pos', use_gpu=True, cache_directory='./cache', tokenize_pretokenized=True, n_process=4)
    return ner_model, pos_model

class Tagger():
    def __init__(self) -> None:
        self.ner_tagger, self.pos_tagger = load_models()

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
        results = [(word.upos, [word.start_char, word.end_char], feature_dicts[i]) for sentence in doc.sentences for i, word in enumerate(sentence.words)]
        return results
    
    def get_ner_tags(self, sentence):
        result = self.ner_tagger.predict(prepare_sentence(sentence), IOBformat=False)
        namedEntities = [(ent["text"], [ent["start_pos"], ent["end_pos"]]) for ent in result["entities"]]
        #words = prepare_sentence(sentence)
        # previous_sentences_len = 0
        # namedEntities = []
        # step_size = 100
        # for i in range(0, len(words), step_size):
        #     result = self.ner_tagger.predict(words[i:i+step_size], IOBformat=False)
        #     namedEntities += [(ent["text"], [ent["start_pos"] + previous_sentences_len, ent["end_pos"] + previous_sentences_len]) for ent in result["entities"]]
        #     previous_sentences_len += len(" ".join(words[i:i+step_size])) + 1
        return namedEntities
    
    # run this function to get all tags
    def get_tags(self, sentence):
        pos = self.get_pos_tags(sentence)
        ner = self.get_ner_tags(sentence)
        return pos, ner