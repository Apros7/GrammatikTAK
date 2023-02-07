# importing external modules
import time
import pandas as pd
from polyleven import levenshtein
import numpy as np
from ast import literal_eval
from transformers import pipeline, Trainer, BertTokenizer
import stanza
import torch
import string
import json
from flask import Flask, request, jsonify

# Time for loading phase:
load_time = time.time()
load_time2 = time.time()

# Create / load dictionary and ngram:
dictionary = pd.read_csv("Datasets/ordlisteFuldform2021rettet.csv")
alphabet = string.ascii_letters
#check_word_word3 = pd.read_csv("Datasets/3GramFrom4Gram-ThirdWordSorted.csv")
check_word_word2 = pd.read_csv("Datasets/4GramFrom5Gram-ThirdWordSorted.csv")

print(f"{time.time()-load_time}")
load_time = time.time()

# Load models
ner_model = pipeline(task='ner', model='saattrupdan/nbailab-base-ner-scandi', aggregation_strategy='first')
#pos_model = stanza.Pipeline("da")

print(f"{time.time()-load_time}")
load_time = time.time()

# Load comma and period model
tokenizer = BertTokenizer.from_pretrained("Maltehb/danish-bert-botxo")
punctuation_model = torch.load("modelCombined2")
punctuation_model.eval()
punctuation_trainer = Trainer(punctuation_model)

print(f"{time.time()-load_time}")
load_time = time.time()

print(f"total time: {time.time() - load_time2}")