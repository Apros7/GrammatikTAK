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

# Track time class
# Used to analyze time used by functions

class TimeTracker():
    def __init__(self):
        self.time = time.time()
        self.time_dict = {}
        self.excess_time = {}
        self.excess_index = 1
    
    def track(self, key):
        if key in self.time_dict.keys():
            self.time_dict[key] += time.time()-self.time
        else:
            self.time_dict[key] = time.time()-self.time

    def __call__(self):
        print(*[item for item in self.time_dict.items()], sep="\n")
        print("Excess time: ")
        print(*[item for item in self.excess_time.items()], sep="\n")
    
    def complete_reset(self):
        self.time = time.time()

    def reset(self, string=None):
        self.excess_time[f"reset{self.excess_index}({string})"] = time.time()-self.time
        self.excess_index += 1
        self.time = time.time()

# Time for loading phase:
load_time = time.time()

# Create / load dictionary and ngram:
dictionary = pd.read_csv("Datasets/ordlisteFuldform2021rettet.csv")
alphabet = string.ascii_letters
check_word_word2 = pd.read_csv("Datasets/3GramFrom4Gram-SecondWordSorted.csv")

# Load models
ner_model = pipeline(task='ner',
                model='saattrupdan/nbailab-base-ner-scandi',
                aggregation_strategy='first')
pos_model = stanza.Pipeline("da")

# Load comma and period model
tokenizer = BertTokenizer.from_pretrained("Maltehb/danish-bert-botxo")
punctuation_model = torch.load("modelCombined2")
punctuation_model.eval()
punctuation_trainer = Trainer(punctuation_model)

# Find out how long each function takes:
best_words_time = []
candidates_time = []

# Display errors:
errors = []

# Iniatiate Time Tracker
timeTracker = TimeTracker()

class Dataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels=None):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        if self.labels:
            item["labels"] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.encodings["input_ids"])

def ner_tagging(sentence):
    result = ner_model(sentence)
    namedEntities = [row["word"] for row in result]
    return namedEntities

def pos_tagging(sentence):
    result = pos_model(sentence)
    lst = []
    for sent in result.sentences:
        for i in range(len(sent.words)):
            lst.append(sent.words[i].upos)
    return lst

def concat_duplicates(lst):
    elements = {}
    unique_lst = []
    for sublist in lst:
        if sublist[2] in elements.keys():
            elements[sublist[2]][1] = sublist[1]
            elements[sublist[2]][3] += " " + sublist[3]
        else:
            elements[sublist[2]] = sublist
    return list(elements.values())

def checkPunctuationErrors(sentence):
    words = sentence.split()
    joined_words = []
    i = 0
    while i < len(words):
        word = words[i]
        if i < len(words) - 1 and words[i + 1] in ".,!?\";:":
            errors.append([word + words[i + 1], word + " " + words[i + 1], i, "Det ser ud til, at dette tegn er sat forkert."])
            word = word + words[i + 1]
            i += 1
        joined_words.append(word)
        i += 1
    new_words = " ".join(joined_words)
    return new_words



def split_sentence(sentence, prev_punc):
    sentences = []
    test_data = []
    words = sentence.split()
    for i in range(len(words)-3):
        test_data.append(" ".join(words[i:i+4]))
    tokenized = tokenizer(test_data, padding=True, truncation=True, max_length=512)
    test_dataset = Dataset(tokenized)
    raw_pred_period, _, _ = punctuation_trainer.predict(test_dataset)
    y_pred_period = np.argmax(raw_pred_period, axis=1)
    last_sentence = 0
    for i in range(len(y_pred_period)):
        if y_pred_period[i] == 1:
            new_sentence = " ".join(words[last_sentence:i+2])
            sentences.append(new_sentence)
            last_sentence = i+2
    sentences.append(" ".join(words[last_sentence:]))
    return sentences, y_pred_period


def correct_punctuation(sentence, prev_punctuation, counter_punc, predicted_punctuation, last_sentence):
    test_data = []
    words = sentence.split()
    prev_punc = counter_punc
    if last_sentence:
        minus = 3
    else:
        minus = 1
    for i in range(len(words)-minus):
        if words[i+1] == words[-1]:
            continue
        current_pred_punc, current_prev_punc = predicted_punctuation[counter_punc], prev_punctuation[counter_punc+1]
        if current_pred_punc == 2:
            if current_prev_punc != 2:
                error = f"Der skal være komma efter \"{words[i+1]}\""
                if current_prev_punc == 0:
                    errors.append([words[i+1], words[i+1] + ",", counter_punc+1, error])
            words[i+1] = words[i+1] + ","
        elif current_prev_punc == 1:
            error_message = f"Der skal ikke være punktum efter {words[i+1]}"
            errors.append([words[i+1] + ".", words[i+1], counter_punc+1, error_message])
        elif current_prev_punc == 2:
            error_message = f"Der skal ikke være komma efter {words[i+1]}"
            errors.append([words[i+1] + ",", words[i+1], counter_punc+1, error_message])
        counter_punc += 1
    counter_punc = len(words) + prev_punc
    if last_sentence:
        minus = 1
    set_period = True
    if prev_punctuation[counter_punc-minus] != 1:
        error = f"Der skal være punktum efter \"{words[-1]}\""
        if prev_punctuation[counter_punc-minus] == 3:
            words[-1] = words[-1] + "?"
            set_period = False
        elif prev_punctuation[counter_punc-minus] == 4:
            words[-1] = words[-1] + "!"
            set_period = False
        elif prev_punctuation[counter_punc-minus] == 2:
            error += " i stedet for et komma."
            errors.append([words[-1], words[-1] + ".", counter_punc-minus, error, 0])
        else:
            errors.append([words[-1], words[-1] + ".", counter_punc-minus, error + ".", 0])
    if set_period:
        words[-1] = words[-1] + "."
    return " ".join(words), counter_punc

    

def capitalize_sentence(sentence, named_entities, pos_dict, prev_big_letters, counter_capitalize, last_word_last_sentence, prev_punctuation):
    words = sentence.split()
    for i in range(len(words)):
        word = words[i]
        prev_big_letter = prev_big_letters[counter_capitalize]
        if i == 0:
            first_word = True
        else:
            first_word = False
        if is_word_number(word):
            counter_capitalize += 1
            continue
        if word in alphabet and word != "i" and word != "I":
            if prev_big_letter:
                words[i] = str.capitalize(word)
            counter_capitalize += 1
            continue
        if first_word or (word in named_entities):
            word_capitalized = str.capitalize(word)
            words[i] = word_capitalized
            if not prev_big_letter and not is_word_number(last_word_last_sentence):
                error = f"\"{word}\" skal begynde med stort bogstav"
                if first_word:
                    error += f", da \"{word}\" er det første ord i en ny sætning."
                else:
                    error += f", da \"{word_capitalized}\" er et egenavn."
                if prev_punctuation[counter_capitalize] == 1:
                    errors.append([word + ".", word_capitalized + ".", counter_capitalize, error])
                else: 
                    errors.append([word, word_capitalized, counter_capitalize, error])
        elif word == "i" and prev_big_letter == False:
            try: next_pos = pos_dict[i]
            except: continue
            if next_pos == "VERB" or next_pos == "AUX":
                words[i] = str.capitalize(word)
                if not prev_big_letter:
                    error = f"\"{word}\" skal begynde med stort bogstav: \"{word_capitalized}\""
                    errors.append([word, word_capitalized, counter_capitalize, error])
        elif prev_big_letter and prev_punctuation[counter_capitalize-1] in [0, 2]:
            error = f"\"{str.capitalize(word)}\" skal ikke begynde med stort bogstav: \"{word}\""
            errors.append([word, word.lower(), counter_capitalize, error])
        counter_capitalize += 1
    capitalized = " ".join(words)
    return capitalized, counter_capitalize, words[-1]


def complete_correction(input_sentence):
    global errors
    errors = []
    timeTracker.reset("Function starts")
    input_sentence = checkPunctuationErrors(input_sentence)
    timeTracker.track("checkPunctuationErrors")
    counter_capitalize, counter_punc, len_prev_sentences, last_word_last_sentence = 0,0,0,"test"
    correct_sentences = []
    sentence, prev_punctuation, prev_big_letters = clean_up_sentence(input_sentence)
    timeTracker.track("CleanUp")
    sentences, predicted_punctuation = split_sentence(sentence, prev_punctuation)
    timeTracker.track("SplitSentence")
    for i in range(len(sentences)):
        timeTracker.reset("For loop starts")
        sentence = sentences[i]
        if i == len(sentences)-1:
            last_sentence = True
        else:
            last_sentence = False
        named_entities = []
        words = sentence.split()
        num_words = 5
        timeTracker.reset("Variables are set")
        for smaller_sentence in [" ".join(sublist) for sublist in [words[i:i+num_words] for i in range(0, len(words), num_words)]]:
            named_entities_partly = ner_tagging(smaller_sentence)
            named_entities += named_entities_partly
        timeTracker.track("NER")
        pos_dict = pos_tagging(sentence)
        named_entities = set(named_entities)
        timeTracker.track("POS")
        no_spell_error, pos_dict, len_prev_sentences = correct_spelling_mistakes(sentence, named_entities, pos_dict, len_prev_sentences)
        timeTracker.track("Spellchecking")
        capitalized_sentence, counter_capitalize, last_word_last_sentence = capitalize_sentence(no_spell_error, named_entities, pos_dict, prev_big_letters, counter_capitalize, last_word_last_sentence, prev_punctuation)
        timeTracker.track("Capitalize")
        complete_sentence, counter_punc = correct_punctuation(capitalized_sentence, prev_punctuation, counter_punc, predicted_punctuation, last_sentence)
        timeTracker.track("Punctuation")
        correct_sentences.append(complete_sentence)
    correct_sentence = " ".join(correct_sentences)
    timeTracker.reset("Done with For loop")
    concat_errors = concat_duplicates(errors)
    timeTracker.track("Concat_duplicates")
    return concat_errors

def is_word_number(word):
    try: int(word); return True
    except: return False

def correct_spelling_mistakes(sentence, named_entities, pos_dict, len_prev_sentences):
    words = sentence.split()
    det_dict = {"en": "et", "et": "en", "den": "det", "det": "den"}
    # Correct misspelled words
    for i in range(0, len(words) - 2):
        current_word = words[i+1]
        if (current_word not in dictionary.values) and (current_word not in named_entities) and (not is_word_number(current_word)):
            # Not the best way to fix i dag and i morgen
            if current_word == "idag" or current_word == "imorgen":
                word = "i dag" if current_word == "idag" else "i morgen"
                error = f"\"{current_word}\" er ikke et gyldigt ord. \"{word}\" passer bedre ind her."
                errors.append([current_word, word, i+2, error, 0])
                continue
            else: 
                word = find_correct_word(words[i], current_word, words[i+2])
            if word == current_word:
                continue
            error = f"\"{current_word}\" er ikke et gyldigt ord. \"{word}\" passer bedre ind her."
            errors.append([current_word, word, i+1, error, 0])
            # pos_dict = fix_pos_dict(word, current_word, pos_dict)
            words[i+1] = word
    #sentence_without_spelling_mistakes = " ".join(words)

    # Suggest better words:
    for i in range(0, len(words) - 2):
        current_pos = pos_dict[i+1]
        if is_word_number(words[i+1]):
            continue
        # words[i+2] is target_word
        if current_pos != "VERB" and current_pos != "DET":
            continue 
        suggestion = find_suggestions(words[i], words[i+1], words[i+2])
        if suggestion == words[i+1]:
            continue
        # hard code / not great but makes things work - should be changed quickly
        if current_pos == "DET":
            if words[i+1] not in det_dict:
                continue
            elif suggestion != det_dict[words[i+1]]:
                continue
        error = f"\"{suggestion}\" passer bedre ind end: \"{words[i+1]}\"."
        errors.append([words[i+1], suggestion, i+1+len_prev_sentences, error, 0])
        words[i+1] = suggestion
    final_sentence = " ".join(words)
    return final_sentence, pos_dict, len_prev_sentences + len(words)

# print statements
# f"Den rettede sætning bliver dermed: \n {final_sentence}.\n\n" \
# f"Uden vores anbefalinger ser sætningen sådan ud:\n{sentence_without_spelling_mistakes}"


def find_correct_word(word1, target_word, word3):
    start = time.time()
    candidates = find_candidate_words(word1, target_word, word3)
    candidates_time.append(time.time() - start)

    start = time.time()
    word = find_best_words_of_candidates(candidates, target_word)
    best_words_time.append(time.time() - start)
    return word

def clean_up_sentence(sentence):
    words = sentence.split()
    punctuation = []
    words = [word for word in words if word != "."]
    big_letters = [True if word[0].isupper() else False for word in words]
    for word in words:
        if word[-1] == ",":
            punctuation.append(2)
        elif word[-1] == ".":
            punctuation.append(1)
        elif word[-1] == "?":
            punctuation.append(3)
        elif word[-1] == "!":
            punctuation.append(4)
        else:
            punctuation.append(0)
    new_words = " ".join([word.strip(".,!?\";:").lower() for word in words])
    return new_words, punctuation, big_letters


def find_best_words_of_candidates(data, target_word):
    # Compute levenshtein distance
    # Could comment on not being able to find error

    levDist = [(probability, word, levenshtein(word, target_word, 2)) for (word, probability) in data
               if levenshtein(word, target_word, 2) < 2]
    # Returning the correct word without errors:
    if len(levDist) == 0:
        return target_word
    minDist = min(levDist, key=lambda x: x[2])
    if len(minDist) == 3:
        return minDist[1]
    return max(minDist)


def find_candidate_words(word1, word2, word3, method="correct"):
    rowFound = (check_word_word2.loc[((check_word_word2["key1"].values == word1) 
            & (check_word_word2["key2"].values == word3))])["value"].values
    if len(rowFound) == 0:
        return [(word2, 0)]
    lst = literal_eval(rowFound[0])
    return lst


def find_suggestions(word1, target_word, word3):
    start = time.time()
    candidates = find_candidate_words(word1, target_word, word3, method="suggest")
    candidates_time.append(time.time() - start)

    start = time.time()
    word = find_best_words_of_candidates(candidates, target_word)
    best_words_time.append(time.time() - start)
    return word

app = Flask(__name__)
CORS(app)
@app.route("/", methods=["POST"])

def index():
    data = request.get_json()
    input = data["sentence"]
    output = complete_correction(input)
    print(output)
    return jsonify(output)

message = """
Stavefejl og andre grammatiske fejl kan påvirke din troværdighed. GrammatikTAK hjælper dig med at finde din stavefejl og andre grammatiske fejl . 

Vi retter også København som københavn og erik. Så er du sikker på at din tekst er grammatisk korrekt og at du dermed giver den bedste indtryk på din læser.
"""
current_errors = complete_correction(message)
#print(current_errors)
timeTracker()
