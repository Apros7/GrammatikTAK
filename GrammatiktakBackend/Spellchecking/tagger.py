from transformers import pipeline, Trainer, BertTokenizer
import stanza

def load_models():
    ner_model = pipeline(task='ner', model='saattrupdan/nbailab-base-ner-scandi', aggregation_strategy='first')
    pos_model = stanza.Pipeline("da", processors='tokenize,pos', use_gpu=True, cache_directory='./cache', tokenize_pretokenized=True, n_process=4)
    return ner_model, pos_model

class Tagger():
    def __init__(self) -> None:
        self.ner_tagger, self.pos_tagger = load_models()
    
    def get_pos_tags(self, sentence):
        return self.pos_tagger(sentence)
    
    def get_ner_tags(self, sentence):
        return self.ner_tagger(sentence)
    
    def get_tags(self, sentence):
        pass