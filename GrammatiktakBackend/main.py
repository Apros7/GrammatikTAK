# initailize the tracker
from Timetracking.timetracker import TimeTracker
time_tracker = TimeTracker()

# import internal modules
from Punctuation.correct_punctuation import PunctuationCorrector
from Spellchecking.tagger import Tagger

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
from flask_cors import CORS

time_tracker.track("import modules")

# initialize correctors:
punctuation_corrector = PunctuationCorrector()
tagger = Tagger()

time_tracker.track("initialize correctors")

def correct_input(input):
    punctuation_errors = punctuation_corrector.correct_punctuation(input)
    pos_tags, ner_tags = tagger.get_tags(input)
    pass

app = Flask(__name__)
CORS(app)
@app.route("/", methods=["POST"])

def index():
    global all_errors, errors, new_lines
    all_errors, errors, new_lines = [], [], []
    data = request.get_json()
    input = data["sentence"]
    output = correct_input(input)
    #print(*output, sep="\n")
    return jsonify(output)

if __name__ == "__main__":
    pass

time_tracker(.5)
my_input = "Hey Christian.<br>Tak for det. Jeg er desværre i skole til, kl 18, så det har jeg ikke mulighed for.<br>Jeg håber at I får en dejlig aften :smile:."
tagger.get_tags(my_input)

time_tracker.track("end")
time_tracker(.5)

