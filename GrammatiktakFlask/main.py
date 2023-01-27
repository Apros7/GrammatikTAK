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
import os

# Time for loading phase:
load_time = time.time()

# Create / load dictionary and ngram:
dictionary = pd.read_csv("Datasets/ordlisteFuldform2021rettet.csv")
alphabet = string.ascii_letters
check_word_word2 = pd.read_csv("Datasets/4GramFrom5Gram-ThirdWordSorted.csv")

# Load models
ner_model = pipeline(task='ner',
                model='saattrupdan/nbailab-base-ner-scandi',
                aggregation_strategy='first')
pos_model = stanza.Pipeline("da")

# Load comma and period model
tokenizer = BertTokenizer.from_pretrained('Maltehb/danish-bert-botxo')
punctuation_model = torch.load("GrammatiktakFlask/modelCombined2")
#punctuation_model = torch.load("GrammatiktakFlask/modelCombined8", map_location=torch.device("cpu"))
punctuation_model.eval()
punctuation_trainer = Trainer(punctuation_model)

# Find out how long each function takes:
best_words_time = []
candidates_time = []

# Display errors:
errors = []

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
    dictionary = {}
    for sent in result.sentences:
        for word in sent.words:
            dictionary[word.text] = word.upos
    return dictionary

def find_errors(new_sentence, old_sentence):
    new_words = [word for word in new_sentence.split()]
    old_words = [word for word in old_sentence.split()] 

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

def split_sentence(sentence):
    sentences = []
    test_data = []
    words = sentence.split()

    # Script for using model with 8 block size and padding

    #padding = "<PAD>"
    #context = [padding] * 3 + words[:5]
    #while len(context) < 8:
    #    context += [padding]
    #for i in range(len(words)):
    #    test_data.append(context)
    #    next_word = padding if i+5 > len(words)-1 else words[i]
    #    context = context[1:] + [next_word] # crop context and append next character
    #test_data = [" ".join(lst) for lst in test_data]

    for i in range(len(words)-3):
        test_data.append(" ".join(words[i:i+4]))

    print(test_data)
    tokenized = tokenizer(test_data, padding=True, truncation=True, max_length=340)
    test_dataset = Dataset(tokenized)
    raw_pred_period, _, _ = punctuation_trainer.predict(test_dataset)
    y_pred_period = np.argmax(raw_pred_period, axis=1)
    last_sentence = 0
    for i in range(len(y_pred_period)):
        if y_pred_period[i] == 1:
            sentences.append(" ".join(words[last_sentence:i+2]))
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
                if current_prev_punc == 1:
                    error += " i stedet for et punktum."
                elif current_prev_punc == 3:
                    error += " i stedet for et spørgsmålstegn."
                elif current_prev_punc == 4:
                    error += " i stedet for et udråbstegn."
                errors.append([words[i+1], words[i+1] + ",", counter_punc+1, error])
            words[i+1] = words[i+1] + ","
        elif current_prev_punc == 1:
            error_message = f"Der skal ikke være punktum efter {words[i+1]}"
            errors.append([words[i+1], (words[i+1])[:-1], counter_punc+1, error_message])
        elif current_prev_punc == 2:
            error_message = f"Der skal ikke være komma efter {words[i+1]}"
            errors.append([words[i+1], (words[i+1])[:-1], counter_punc+1, error_message])
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
            errors.append([words[-1], words[-1] + ".", counter_punc-minus, error])
        else:
            errors.append([words[-1], words[-1] + ".", counter_punc-minus, error + "."])
    if set_period:
        words[-1] = words[-1] + "."
    return " ".join(words), counter_punc

    

def capitalize_sentence(sentence, named_entities, pos_dict, prev_big_letters, counter_capitalize, last_word_last_sentence):
    words = sentence.split()
    # missing capitalizing after full stop
    for i in range(len(words)):
        word = words[i]
        prev_big_letter = prev_big_letters[counter_capitalize]
        if i == 0:
            first_word = True
        else:
            first_word = False
        if not is_word_number(word):
            counter_capitalize += 1
            continue
        if word in alphabet:
            if prev_big_letter:
                words[i] = str.capitalize(word)
            counter_capitalize += 1
            continue
        if first_word or (word in named_entities):
            word_capitalized = str.capitalize(word)
            words[i] = word_capitalized
            if not prev_big_letter and not is_word_number(last_word_last_sentence):
                error = f"\"{word}\" skal begynde med stort bogstav: \"{word_capitalized}\""
                if first_word:
                    error += f", da \"{word}\" er det første ord i en ny sætning."
                else:
                    error += f", da \"{word_capitalized}\" er et egenavn."
                errors.append([word, word_capitalized,counter_capitalize, error])
        elif word == "i":
            try: next_pos = pos_dict[words[i+1]]
            except: continue
            if next_pos == "VERB" or next_pos == "AUX":
                words[i] = str.capitalize(word)
                if not prev_big_letter:
                    error = f"\"{word}\" skal begynde med stort bogstav: \"{word_capitalized}\""
                    errors.append([word, word_capitalized, counter_capitalize, error])
        elif prev_big_letter:
            error = f"\"{str.capitalize(word)}\" skal ikke begynde med stort bogstav: \"{word}\""
            errors.append([word, word.lower(), counter_capitalize, error])
        counter_capitalize += 1
    capitalized = " ".join(words)
    return capitalized, counter_capitalize, words[-1]

def complete_correction(input_sentence):
    global errors
    errors = []
    counter_capitalize, counter_punc, last_word_last_sentence = 0,0, "test"
    correct_sentences = []
    sentence, prev_punctuation, prev_big_letters = clean_up_sentence(input_sentence)
    sentences, predicted_punctuation = split_sentence(sentence)
    for i in range(len(sentences)):
        sentence = sentences[i]
        if i == len(sentences)-1:
            last_sentence = True
        else:
            last_sentence = False
        named_entities = ner_tagging(sentence)
        pos_dict = pos_tagging(sentence)
        no_spell_error, pos_dict = correct_spelling_mistakes(sentence, named_entities, pos_dict)
        capitalized_sentence, counter_capitalize, last_word_last_sentence = capitalize_sentence(no_spell_error, named_entities, pos_dict, prev_big_letters, counter_capitalize, last_word_last_sentence)
        complete_sentence, counter_punc = correct_punctuation(capitalized_sentence, prev_punctuation, counter_punc, predicted_punctuation, last_sentence)
        correct_sentences.append(complete_sentence)
    correct_sentence = " ".join(correct_sentences)
    concat_errors = concat_duplicates(errors)
    return concat_errors

def fix_pos_dict(word, old_word, pos_dict):
    value = pos_dict[old_word]
    del pos_dict[old_word]
    pos_dict[word] = value
    return pos_dict

def is_word_number(word):
    return word.isalpha()

def correct_spelling_mistakes(sentence, named_entities, pos_dict):
    words = sentence.split()
    # Correct misspelled words
    for i in range(0, len(words) - 2):
        current_word = words[i+2]
        if (current_word not in dictionary.values) and (current_word not in named_entities) and (not is_word_number(current_word)):
            word = find_correct_word(words[i], words[i+1], current_word)
            if word == current_word:
                continue
            error = f"\"{current_word}\" er ikke et gyldigt ord. \"{word}\" passer bedre ind her."
            errors.append([current_word, word, i+2, error])
            pos_dict = fix_pos_dict(word, current_word, pos_dict)
            words[i+2] = word
    #sentence_without_spelling_mistakes = " ".join(words)
    
    # Suggest better words:
    for i in range(0, len(words) - 3):
        current_pos = pos_dict[words[i+1]]
        if is_word_number(words[i+1]):
            continue
        # words[i+1] is target_word
        if current_pos != "VERB" and current_pos != "DET":
            continue 
        suggestion = find_suggestions(words[i], words[i+1], words[i+2], words[i+3])
        if suggestion == words[i+2]:
            continue
        error = f"\"{suggestion}\" passer bedre ind end: \"{words[i+2]}\"."
        errors.append([words[i+2], suggestion, i+2, error])
        pos_dict = fix_pos_dict(suggestion, words[i+1], pos_dict)
        words[i+1] = suggestion
    final_sentence = " ".join(words)
    return final_sentence, pos_dict

# print statements
# f"Den rettede sætning bliver dermed: \n {final_sentence}.\n\n" \
# f"Uden vores anbefalinger ser sætningen sådan ud:\n{sentence_without_spelling_mistakes}"


def find_correct_word(word1, word2, target_word):
    start = time.time()
    candidates = find_candidate_words(word1, word2, target_word, None)
    candidates_time.append(time.time() - start)

    start = time.time()
    word = find_best_words_of_candidates(candidates, target_word)
    best_words_time.append(time.time() - start)
    return word

def clean_up_sentence(sentence):
    words = sentence.split()
    punctuation = []
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
    return " ".join([word.strip(".,!?\";:").lower() for word in words]), punctuation, big_letters


def find_best_words_of_candidates(data, target_word):
    # Compute levenshtein distance
    # Could comment on not being able to find error

    levDist = [(probability, word, levenshtein(word, target_word, 2)) for (word, probability) in data
               if levenshtein(word, target_word, 2) < 3]
    # Returning the correct word without errors:
    if len(levDist) == 0:
        return target_word
    minDist = min(levDist, key=lambda x: x[2])
    if len(minDist) == 3:
        return minDist[1]
    return max(minDist)


def find_candidate_words(word1, word2, word3, word4, method="correct"):
    if method == "correct":
        rowFound = (check_word_word2.loc[((check_word_word2["key2"].values == word1) 
        & (check_word_word2["key3"].values == word2))])["value"].values
    else:
        rowFound = check_word_word2.loc[((check_word_word2["key1"].values == word1) 
        & (check_word_word2["key2"].values == word2) & (check_word_word2["key3"].values == word4))].values

    if len(rowFound) == 0:
        return [(word2, 0)]
    if method == "correct":
        full_list = []
        items = []
        for list in rowFound:
            new_list = literal_eval(list)
            for element in new_list:
                if element[0] not in items:
                    full_list.append(element)
                    items.append(element[0])
        return full_list
    else:
        lst = literal_eval(rowFound[0][3])
    return lst


def find_suggestions(word1, word2, target_word, word4):
    start = time.time()
    candidates = find_candidate_words(word1, word2, target_word, word4, method="suggest")
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
    return jsonify(output)

print(complete_correction("hej jeg hedder per"))