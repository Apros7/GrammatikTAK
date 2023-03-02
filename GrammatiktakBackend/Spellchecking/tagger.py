from transformers import pipeline, Trainer, BertTokenizer
import stanza

def load_models():
    ner_model = pipeline(task='ner', model='saattrupdan/nbailab-base-ner-scandi', aggregation_strategy='first')
    pos_model = stanza.Pipeline("da", processors='tokenize,pos', use_gpu=True, cache_directory='./cache', tokenize_pretokenized=True, n_process=4)
    return ner_model, pos_model

def find_index(all_words_from_sentence, index_of_word_in_all_words, word):
    start_index = sum([len(word) for word in all_words_from_sentence[:index_of_word_in_all_words]]) + len(all_words_from_sentence[:index_of_word_in_all_words])
    end_index = start_index + len(word) - 1
    return [start_index, end_index]

class Tagger():
    def __init__(self) -> None:
        self.ner_tagger, self.pos_tagger = load_models()

    def get_pos_tags(self, sentence):
        doc = self.pos_tagger(sentence)
        results = [(word.upos, [word.start_char, word.end_char]) for sentence in doc.sentences for word in sentence.words]
        return results
    
    def get_ner_tags(self, sentence):
        result = self.ner_tagger(sentence.split())
        namedEntities = [(result[i][0]["word"], find_index(sentence.split(), i, result[i][0]["word"])) for i in range(len(result)) if len(result[i]) > 0 ]
        return namedEntities
    
    # run this function to get all tags
    def get_tags(self, sentence):
        return self.get_pos_tags(sentence), self.get_ner_tags(sentence)