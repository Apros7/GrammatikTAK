from transformers import pipeline
import pandas as pd


def find_cap_words(sentence):
    ner = pipeline(task='ner',
                   model='saattrupdan/nbailab-base-ner-scandi',
                   aggregation_strategy='first')
    result = ner(sentence)
    namedEntities = [row["word"] for row in result]
    return namedEntities