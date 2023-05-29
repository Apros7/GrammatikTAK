from transformers import pipeline
import pandas as pd
from danlp.models import load_bert_ner_model
from transformers import AutoTokenizer, ElectraModel
import time

def check_inactive(func):
    def wrapper(self, *args, **kwargs):
        if self.inactive:
            return
        return func(self, *args, **kwargs)
    return wrapper

class TimeTracker():
    def __init__(self):
        self.time = time.time()
        self.time2 = time.time()
        self.time_dict = {}
        self.time_dict2 = {}
        self.excess_time = {}
        self.excess_index = 1
        self.inactive = False

    @check_inactive
    def track(self, key):
        if key in self.time_dict.keys():
            self.time_dict[key] += time.time()-self.time
        else:
            self.time_dict[key] = time.time()-self.time
        self.time = time.time()
    
    @check_inactive
    def track2(self, key):
        if key in self.time_dict2.keys():
            self.time_dict2[key] += time.time()-self.time2
        else:
            self.time_dict2[key] = time.time()-self.time2
        self.time2 = time.time()

    @check_inactive
    def __call__(self, bound=.5):
        time_taken = ["HIGH" if value > bound else "LOW " for value in self.time_dict.values()]
        print(*zip(time_taken, [item for item in self.time_dict.items()]), sep="\n")
        print("Full Function", *[item for item in self.time_dict2.items()], sep="\n")
        print("Excess time:", *[item for item in self.excess_time.items()], sep="\n")
    
    @check_inactive
    def complete_reset(self):
        self.time = time.time()
        self.time2 = time.time()

    @check_inactive
    def reset(self, string=None):
        self.excess_time[f"reset{self.excess_index}({string})"] = time.time()-self.time
        self.excess_index += 1
        self.time = time.time()


ner_model = load_bert_ner_model()

ner = pipeline(task='ner',
                model='saattrupdan/nbailab-base-ner-scandi',
                aggregation_strategy='first')

electra = pipeline(task="ner", model= "Maltehb/aelaectra-danish-electra-small-cased-ner-dane")

timeTracker = TimeTracker()

def find_cap_words1(sentence):
    result = ner(sentence)
    namedEntities = [row["word"] for row in result]
    return namedEntities

timeTracker.track("Base NER Scandi")

def find_cap_words2(sentence):
    words = sentence.split(" ")
    result = ner_model.predict(words, IOBformat=False)
    namedEntities = [ent["text"] for ent in result["entities"]]
    return namedEntities

timeTracker.track("Current NER model")

def find_cap_words3(sentence):
    result = electra(sentence)
    namedEntities = [row["word"] for row in result]
    return namedEntities

timeTracker.track("Ælectra model")


sentence = """

I den maleriske by Aarhus, beliggende på Østjylland-kysten, finder du en perlerække af spændende steder, virksomheder og navne, der giver byen sin unikke karakter.

Start din dag med en lækker morgenmad på det populære cafésted, "Smørrebrødsbaren", hvor du kan nyde klassiske danske smørrebrødsspecialiteter som "hønsesalat" og "leverpostej". Efter at have fået fyldt maven kan du gå en tur langs Aarhus Havn og beundre det moderne arkitekturvidunder, Aarhus Ø, hvor du finder virksomheder som "Innovatech" og "Aarhus Shipping".

Hvis du er kunstinteresseret, bør du besøge "ARoS", byens berømte kunstmuseum, der huser værker af både danske og internationale kunstnere. Efter en kulturel oplevelse kan du tage en shoppingtur i "Strøget", Aarhus' mest populære shoppinggade, hvor du finder butikker som "H&M", "Magasin" og "Illum".
"""

NER = ["Aarhus", "Østjylland", "Smørrebrødsbaren", "Aarhus Havn", "Aarhus Ø", "Innovatech", 
        "Aarhus Shipping", "ARoS", "Strøget", "Magasin", "H&M", "Illum", "Aarhus'"]

print("NER scandi: ")
print(find_cap_words1(sentence))
print("Current model: ")
print(find_cap_words2(sentence))
print("Ælectra model: ")
print(find_cap_words3(sentence))

print(timeTracker())