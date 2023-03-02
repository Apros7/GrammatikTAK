from transformers import pipeline, Trainer, BertTokenizer
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

    def get_pos_tags(self, sentence):
        doc = self.pos_tagger(sentence)
        results = [(word.upos, [word.start_char, word.end_char]) for sentence in doc.sentences for word in sentence.words]
        return results
    
    def get_ner_tags(self, sentence):
        result = self.ner_tagger.predict(prepare_sentence(sentence), IOBformat=False)
        namedEntities = [(ent["text"], [ent["start_pos"], ent["end_pos"]]) for ent in result["entities"]]
        return namedEntities
    
    # run this function to get all tags
    def get_tags(self, sentence):
        pos = self.get_pos_tags(sentence)
        ner = self.get_ner_tags(sentence)
        return pos, ner