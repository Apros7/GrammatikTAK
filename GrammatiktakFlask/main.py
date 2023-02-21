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
from Helper_functions.TimeTracker import TimeTracker

# Time for loading phase:
load_time = time.time()

# Create / load dictionary and ngram:
dictionary = pd.read_csv("Datasets/ordlisteFuldform2021OneRow.csv")
alphabet = string.ascii_letters
check_word_word2 = pd.read_csv("Datasets/3GramFrom4Gram-SecondWordSorted.csv")

# Load models
ner_model = pipeline(task='ner',
                model='saattrupdan/nbailab-base-ner-scandi',
                aggregation_strategy='first')
pos_model = stanza.Pipeline("da", processors='tokenize,pos', use_gpu=True, cache_directory='./cache', tokenize_pretokenized=True, n_process=4)

# Load comma and period model
tokenizer = BertTokenizer.from_pretrained("Maltehb/danish-bert-botxo")
punctuation_model = torch.load("modelCombined2")
punctuation_model.eval()
punctuation_trainer = Trainer(punctuation_model)

# Find out how long each function takes:
best_words_time = []
candidates_time = []

# Display errors:
all_errors = []
errors = []
new_lines = []

# Iniatiate Time Tracker
timeTracker = TimeTracker()
#timeTracker.inactive = True

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

def pos_tag_sentence(sentence_group):
    doc = pos_model(sentence_group)
    results = []
    for sentence in doc.sentences:
        sentence_results = []
        for word in sentence.words:
            sentence_results.append(word.pos)
        results.append(sentence_results)
    return results

def pos_tagging(group_of_sentences):
    tagged_sentences = []
    for group in group_of_sentences:
        results = pos_tag_sentence(group)
        tagged_sentences.append(results)
    return tagged_sentences


def concat_duplicates(lst):
    elements = {}
    for sublist in lst:
        if sublist[2] in elements.keys():
            elements[sublist[2]][1] = sublist[1]
            elements[sublist[2]][3] += " " + sublist[3]
        else:
            elements[sublist[2]] = sublist
    return list(elements.values())

def order_errors(error_lst):
    return sorted(error_lst, key=lambda x: x[2])

def checkPunctuationErrors(sentence):
    words = sentence.split()
    joined_words = []
    i = 0
    while i < len(words):
        word = words[i]
        if i < len(words) - 1 and words[i + 1] in ".,!?\";:":
            errors.append([word + " " + words[i + 1], word + words[i + 1], i, "Det ser ud til, at dette tegn er sat forkert."])
            word = word + words[i + 1]
            i += 1
        joined_words.append(word)
        i += 1
    new_words = " ".join(joined_words)
    return new_words

def split_sentences_by_newline(sentence):
    list_of_words = sentence.split("<br>")
    sublists = []
    i = -1
    for words in list_of_words:
        sublists.append(" ".join([word.strip() for word in words.split()]))
        i += len(words.split()) if words.find(" ") >= 0 else 1
        new_lines.append(i)
    sublists = [s for s in sublists if s]
    return sublists

def correct_error_indexes(prev_sentences_len):
    for error in errors:
        error[2] += prev_sentences_len
    all_errors.extend(errors)

def add_newlines(lst):
    for sublst in lst:
        if len(sublst) >= 3 and sublst[2] in new_lines:
            sublst[0] += "<br>"
            sublst[1] += "<br>"
    return lst

def split_sentence(sentence):
    sentences = []
    test_data = []
    words = sentence.split()
    if sentence.find(" ") < 0:
        return [sentence], []
    for i in range(len(words)-3):
        test_data.append(" ".join(words[i:i+4]))   
    if test_data == []:
        return [sentence], []
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
    words = sentence.split()
    prev_punc = counter_punc
    if last_sentence:
        minus = 3
    else:
        minus = 1
    for i in range(len(words)-minus):
        if i+1 == len(words):
            continue
        current_pred_punc = predicted_punctuation[counter_punc]
        current_prev_punc = prev_punctuation[counter_punc+1]
        if current_pred_punc == 2:
            if current_prev_punc != 2:
                error = f"Der skal være komma efter \"{words[i+1]}\""
                if current_prev_punc == 0:
                    errors.append([words[i+1], words[i+1] + ",", counter_punc+1, error])
            words[i+1] = words[i+1] + ","
        #elif current_prev_punc == 1:
        #    error_message = f"Der skal ikke være punktum efter {words[i+1]}"
        #    errors.append([words[i+1] + ".", words[i+1], counter_punc+1, error_message])
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
            errors.append([words[-1], words[-1] + ".", counter_punc-minus, error])
        else:
            errors.append([words[-1], words[-1] + ".", counter_punc-minus, error + "."])
    if set_period:
        words[-1] = words[-1] + "."
    return " ".join(words), counter_punc

    

def capitalize_sentence(sentence, named_entities, pos_dict, prev_big_letters, counter_capitalize, last_word_last_sentence, prev_punctuation):
    words = sentence.split() if sentence.find(" ") >= 0 else [sentence]
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


def complete_correction(complete_sentence):
    global errors
    errors = []
    timeTracker.complete_reset()
    previous_sentences_len = 0
    input_sentences = split_sentences_by_newline(complete_sentence)
    groups_of_sentences, predicted_punctuations, prev_punctuations, group_prev_big_letters = [], [], [], []
    
    for i in range(len(input_sentences)):
        input_sentence = input_sentences[i]
        input_sentence = checkPunctuationErrors(input_sentence)
        timeTracker.track("checkPunctuationErrors")
        sentence, prev_punctuation, prev_big_letters = clean_up_sentence(input_sentence)
        prev_punctuations.append(prev_punctuation)
        group_prev_big_letters.append(prev_big_letters)
        timeTracker.track("CleanUp")
        sentences, predicted_punctuation = split_sentence(sentence)
        groups_of_sentences.append(sentences)
        predicted_punctuations.append(predicted_punctuation)
        timeTracker.track("SplitSentence")

    pos_dicts = pos_tagging(groups_of_sentences)
    timeTracker.track("POS")

    for x in range(len(input_sentences)):
        counter_capitalize, len_prev_sentences, counter_punc, last_word_last_sentence = 0,0,0,"test"
        sentences = groups_of_sentences[x]
        predicted_punctuation = predicted_punctuations[x]
        prev_big_letters = group_prev_big_letters[x]
        prev_punctuation = prev_punctuations[x]

        for i in range(len(sentences)):
            sentence = sentences[i]
            if i == len(sentences)-1:
                last_sentence = True
            else:
                last_sentence = False
            named_entities = []
            words = sentence.split()
            num_words = 10
            timeTracker.track("Variables are set")
            for smaller_sentence in [" ".join(sublist) for sublist in [words[i:i+num_words] for i in range(0, len(words), num_words)]]:
                named_entities_partly = ner_tagging(smaller_sentence)
                named_entities += named_entities_partly
            timeTracker.track("NER")
            pos_dict = pos_dicts[x][i]
            named_entities = set(named_entities)
            timeTracker.track("POS_set")
            no_spell_error, pos_dict, len_prev_sentences = correct_spelling_mistakes(sentence, named_entities, pos_dict, len_prev_sentences)
            timeTracker.track("Spellchecking")
            capitalized_sentence, counter_capitalize, last_word_last_sentence = capitalize_sentence(no_spell_error, named_entities, pos_dict, prev_big_letters, counter_capitalize, last_word_last_sentence, prev_punctuation)
            timeTracker.track("Capitalize")
            complete_sentence, counter_punc = correct_punctuation(capitalized_sentence, prev_punctuation, counter_punc, predicted_punctuation, last_sentence)
            timeTracker.track("Punctuation")
        timeTracker.reset("Done with For loop")
        correct_error_indexes(previous_sentences_len)
        previous_sentences_len += len(input_sentence.split()) if input_sentence.find(" ") >= 0 else 1
        errors = []
    concat_errors = concat_duplicates(all_errors)
    timeTracker.track("Concat_duplicates")
    all_errors_with_newlines = add_newlines(concat_errors)
    timeTracker.track2("Function Complete")
    ordered_errors = order_errors(all_errors_with_newlines)
    return ordered_errors

def is_word_number(word):
    try: int(word); return True
    except: return False

correct_time = []
suggest_time = []

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
                errors.append([current_word, word, i+2, error])
                continue
            else: 
                word = find_correct_word(words[i], current_word, words[i+2])
                #word = current_word
            if word == current_word:
                continue
            error = f"\"{current_word}\" er ikke et gyldigt ord. \"{word}\" passer bedre ind her."
            errors.append([current_word, word, i+1, error])
            # pos_dict = fix_pos_dict(word, current_word, pos_dict)
            words[i+1] = word

    # Suggest better words:
    for i in range(0, len(words) - 2):
        current_pos = pos_dict[i+1]
        if is_word_number(words[i+1]):
            continue
        # words[i+2] is target_word
        if current_pos != "VERB" and current_pos != "DET":
            continue 
        suggestion = find_suggestions(words[i], words[i+1], words[i+2])
        #suggestion = words[i+1]
        if suggestion == words[i+1]:
            continue
        # hard code / not great but makes things work - should be changed quickly
        if current_pos == "DET":
            if words[i+1] not in det_dict:
                continue
            elif suggestion != det_dict[words[i+1]]:
                continue
        error = f"\"{suggestion}\" passer bedre ind end: \"{words[i+1]}\"."
        errors.append([words[i+1], suggestion, i+1+len_prev_sentences, error])
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

mask_model_time = []

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
    global all_errors, errors, new_lines
    all_errors, errors, new_lines = [], [], []
    data = request.get_json()
    input = data["sentence"]
    output = complete_correction(input)
    #print(*output, sep="\n")
    return jsonify(output)

message = "En anden form for bias er confirmation bias, hvor man som forsker vægter undersøgelser som understøtter ens hypotese end undersøgelser som vil modsige ens hypotese. Det omfatter også, at hvis man har en vis forventning af et bestemt præparat virkning, at man i så fald også vil fortolke ens data på en måde som understøtter ens forventning. Confirmation bias kan også påvirke ens testpersoner, hvis man ikke er opmærksom på dette. Fx hvis man giver en testperson et præparat som testpersonen forventer har en effekt, vil dette kunne påvirke testpersonens opfattelse af stoffets virkning, på en måde som igen understøtter ens forventning. I det sidstnævnte eksempel er det placeboeffekten som vil kunne give patienten en fornemmelse af at præparatet virker selvom det ikke nødvendigvis er tilfældet. For at modvirker confirmation bias kan man foretage sig af blinding i tre forskellige grader. Ved almindelig blinding ved selve deltagerne i studiet ikke om de modtager den aktuelle behandling eller om de ikke gør, fx ved at give en kalkpille eller lign. Dette er med til at modvirke patientens egne forventninger til behandlingen. Dertil er der også dobbeltblinding hvor hverken patienten eller personalet ved om den behandling de får/giver er den faktiske behandling eller blot placebo. Dette er med til at modvirke at personalets forventning til behandlingen videregives ubevidst under kommunikation. Til sidst kan man også tripelblinde, der lægges til de to tidligere med at dem som behandlinger og analyser data fra studiet ikke ved hvilken gruppe som har modtaget den faktiske behandling. Disse tre former for blinding bidrager til at mindske mængden af confirmation bias mest muligt."
current_errors = complete_correction(message)
print(len(current_errors))
# print(new_lines)

# Tracking time:

timeTracker(.5)

# Reasons for some functions being slow:
# SplitSentence: BERT model predicting punctuation
# POS: Stanza POS model very slow..?? 1/3 of total time spent here.
# Spellchecking: 1/3 of total time spent here.
    # Candidates seems extra slow: 1/2 of spellchecking time is spent here. Mask model could help.

# Could make one model for finding NER and POS in one to save time. Maybe also smaller then Stanza model (or faster in some other way)
# Could also maybe use dacy? https://github.com/centre-for-humanities-computing/DaCy
