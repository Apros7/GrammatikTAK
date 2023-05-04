import pandas as pd
import os
import torch
from transformers import Trainer, BertTokenizer
import numpy as np

test_sentences_verbs = pd.read_csv("Datasets/EuroparlNutidsr_testset.csv", sep=";")

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

import pickle
import string

def find_index(all_words_from_sentence, index_of_word_in_all_words, word):
    start_index = sum([len(word) for word in all_words_from_sentence[:index_of_word_in_all_words]]) + len(all_words_from_sentence[:index_of_word_in_all_words])
    end_index = start_index + len(word)
    return [start_index, end_index]

def clean_sentence(sentence):
    words = sentence.split()
    cleaned_words = []
    for word in words:
        if all(char in string.punctuation for char in word):
            cleaned_words.append(word)
        else:
            cleaned_word = word.translate(str.maketrans("", "", string.punctuation))
            cleaned_words.append(cleaned_word)
    sentence = " ".join(cleaned_words)
    return sentence

def prepare_sentence(sentence, lowercase=True, split_sentences=False, clean=False) -> str:
    if clean:
        sentence = clean_sentence(sentence)
    if split_sentences:
        sentences = sentence.split("<br>")
        return [sent.split() for sent in sentences]
    elif lowercase: 
        return sentence.replace("<br>", " ").lower().split()
    return sentence.replace("<br>", " ").split()

from transformers import pipeline
import tqdm
tqdm.disable = True

def load_model(path):
    device = "mps"
    torch.device(device)
    classifier = torch.load(path, map_location=torch.device('cpu'))
    classifier.eval()
    classifier.to(device)
    return Trainer(classifier)

class NutidsRCorrector():
    def __init__(self, model, pos, padding):
        self.can_verb_be_checked = pickle.load(open("Datasets/nutids_r_stem.pickle", "rb"))
        self.get_tense_from_verb = pickle.load(open("Datasets/nutids_r_bøjninger.pickle", "rb"))
        self.classifier = model
        self.padding = padding
        self.pos = pos
        self.tokenizer = BertTokenizer.from_pretrained('Maltehb/danish-bert-botxo')
        self.buffer = []

    def should_be_nutidsr(self, verbs_to_check):
        dataset = self.make_dataset(verbs_to_check)
        if len(dataset) < 1:
            return [None]*len(verbs_to_check)
        tokenized = self.tokenize_sentences(dataset)
        dataloader = self.convert_dataset_to_dataloader(tokenized)
        predictions = self.get_predictions(dataloader)
        return list(self.turn_predictions_to_bool(predictions, verbs_to_check))

    def turn_predictions_to_bool(self, predictions, verbs_to_check):
        prediction_index = 0
        for i in range(len(verbs_to_check)):
            if verbs_to_check[i]:
                if predictions[prediction_index][1] < 0.95:
                    yield None
                
                elif predictions[prediction_index][0] == 0:
                    yield True
                else:
                    yield False
                prediction_index += 1
            else:
                yield None

    def convert_dataset_to_dataloader(self, dataset):
        test_dataset = Dataset(dataset)
        return test_dataset
    
    def tokenize_sentences(self, sentences):
        X_tokenized = self.tokenizer(sentences, padding=True, truncation=True, max_length=26)
        return X_tokenized
    
    def get_predictions(self, dataloader):
        raw_predictions, _, _ = self.classifier.predict(dataloader)
        scores = torch.softmax(torch.from_numpy(raw_predictions), dim=1)
        max_scores, final_prediction = torch.max(scores, dim=1)
        final_prediction = np.argmax(raw_predictions, axis=1)
        return [(p, s) for p, s in zip(final_prediction, max_scores)]

    def make_dataset(self, verbs_to_check):
        pos_with_padding = ["<PAD>"]*self.padding + [p[0] for p in self.pos] + ["<PAD>"]*self.padding
        dataset = []
        for i in range(len(verbs_to_check)):
            if verbs_to_check[i]:
                dataset.append(" ".join(pos_with_padding[i:i+2*self.padding+1]))
        return dataset

    def verbs_to_check(self, words):
        pos = self.pos
        verbs = []
        for i in range(len(pos)):
            if pos[i][0] != "VERB":
                verbs.append(False)
            elif "Tense" not in pos[i][2].keys():
                verbs.append(False)
            elif pos[i][2]["Tense"] != "Pres":
                verbs.append(False)
            else:
                verbs.append(True)
        for i, bool in enumerate(verbs):
            if not bool:
                continue
            word = words[i].strip(",.!?():;")
            try: stemmed_verb = self.can_verb_be_checked[word]
            except: verbs[i] = False; continue
        return verbs
    
    def is_verbs_nutids_r(self, words, verbs_to_check):
        is_nutids_r = []
        for word, should_check in zip(words, verbs_to_check):
            word = word.strip(",.!?():;")
            if not should_check:
                is_nutids_r.append(None)
                continue
            infinitiv_form, nutids_r_form = self.get_tense_from_verb[self.can_verb_be_checked[word]]
            if word == infinitiv_form:
                is_nutids_r.append(False)
            elif word == nutids_r_form:
                is_nutids_r.append(True)
            else:
                print("ERROR: word is not infinitiv or nutids_r")
                is_nutids_r.append(None)
        return is_nutids_r
    
    def make_nutids_r_error_message(self, word_to_correct, all_words_from_sentence, index_of_word_in_all_words, correct_word, to_nutids_r):
        previous_index = find_index(all_words_from_sentence, index_of_word_in_all_words, word_to_correct)
        nutids_r_comment = " med nutids-r"
        if to_nutids_r:
            # None kan erstattes med "med nutids-r", hvis forskellen er et nutids-r
            description = f"{word_to_correct} skal stå i ___ form{nutids_r_comment}, så der står {correct_word}"
        else: 
            description = f"{word_to_correct} skal stå i ___ form{nutids_r_comment}, så der står {correct_word}"
        return [word_to_correct, correct_word, previous_index, description]

    def make_error_messages(self, words, should_be_nutids_r, is_nutids_r, verbs_to_check):
        errors = []
        for i in range(len(words)):
            if len(words[i].strip(",.!?():;")) == 0:
                continue
            verb_to_check = verbs_to_check[i]
            if not verb_to_check:
                continue 
            current_word = words[i].strip(",.!?():;")
            should_be = should_be_nutids_r[i]
            is_nutid = is_nutids_r[i]
            if should_be == is_nutid or is_nutid is None:
                continue
            stemmed_word = self.can_verb_be_checked[current_word]
            if should_be is True:
                to_nutids_r = True
                correct_word = self.get_tense_from_verb[stemmed_word][1]
            else:
                correct_word = self.get_tense_from_verb[stemmed_word][0]
                to_nutids_r = False
            correct_word = words[i].replace(current_word, correct_word)
            error = self.make_nutids_r_error_message(words[i], words, i, correct_word, to_nutids_r)
            errors.append(error)
        return errors

    def correct(self, sentence, correct_sentence):
        words = prepare_sentence(sentence, lowercase=True)
        verbs_to_check = self.verbs_to_check(words)
        is_nutids_r = self.is_verbs_nutids_r(words, verbs_to_check)
        should_be = self.should_be_nutidsr(verbs_to_check)
        errors = self.make_error_messages(words, should_be, is_nutids_r, verbs_to_check)
        wrong, correct, no_guess = self.get_measures(errors, verbs_to_check, should_be, sentence, correct_sentence)
        return errors, (wrong, correct, no_guess, self.buffer)

    def get_measures(self, errors, verbs_to_check, should_be_nutids, current_sentence, correct_sentence):
        for error in errors:
            current_sentence = current_sentence[:error[2][0]] + error[1] + current_sentence[error[2][1]:]
            diff = len(error[1]) - len(error[0])
            for error in errors:
                error[2] = (error[2][0] + diff, error[2][1] + diff)

        prediction_words = current_sentence.split()
        actual_words = correct_sentence.split()
        wrong, correct, no_guess = 0, 0, 0
            
        for i in range(len(actual_words)):
            actual_word = actual_words[i]
            prediction_word = prediction_words[i]
            should_print = False
            if actual_word != prediction_word:
                if verbs_to_check[i] and should_be_nutids[i] is not None:
                    wrong += 1
                    should_print = True
                else:
                    no_guess += 1
            else: 
                if verbs_to_check[i]:
                    correct += 1

            if should_print:
                print(correct_sentence)
                print(current_sentence)
        
        return wrong, correct, no_guess

import stanza

class Tester():
    def __init__(self, models) -> None:
        self.models =  models
        self.x = test_sentences_verbs["wrong"]
        self.y = test_sentences_verbs["correct"]
        self.pos = self.get_pos()

    def get_pos_tags(self, sentence):
        doc = self.pos_tagger(sentence)
        features = [word.feats if word.feats else None for sentence in doc.sentences for word in sentence.words]
        feature_dicts = self.turn_features_to_dicts(features)
        results = [(word.upos, [word.start_char, word.end_char], feature_dicts[i]) for sentence in doc.sentences for i, word in enumerate(sentence.words)]
        return results

    def turn_features_to_dicts(self, features):
        feature_dicts = []
        current_tense = None
        for feature in features:
            if feature is None:
                feature_dicts.append({})
                continue
            feature_dict = {}
            current_features = feature.split("|")
            for current_feature in current_features:
                key, value = current_feature.split("=")
                if key == "Tense" and current_tense is None:
                    current_tense = value
                feature_dict[key] = value
            if "Tense" not in feature_dict and "VerbForm" in feature_dict and key is not None:
                feature_dict["Tense"] = "Pres" if current_tense is None else current_tense
            feature_dicts.append(feature_dict)
        return feature_dicts

    def get_pos(self):
        with open("FineTuneModels/pos_caching.pkl", "rb") as f:
            pos_list = pickle.load(f)
        if len(pos_list) != len(self.x):
            pos_list = []
            self.pos_tagger = stanza.Pipeline("da", processors='tokenize,pos', use_gpu=True, cache_directory='./cache', tokenize_pretokenized=True, n_process=4)
            for sentence in (self.x):
                pos = self.get_pos_tags(sentence)
                pos_list.append(pos)
            print(len(pos_list))
            print("Updating")
            with open("FineTuneModels/pos_caching.pkl", "wb") as f:
                pickle.dump(pos_list, f)
            print("Updated")
        else:
            print("pos_caching.pkl already exists")
        return pos_list
    
    def test_one_model(self, model):
        total_wrong, total_correct, total_no_guess = 0,0,0
        total_buffer = []
        for i in range(len(self.x)):
            x, y, pos = self.x[i], self.y[i], self.pos[i]
            corrector = NutidsRCorrector(model, pos, 5)
            errors, (wrong, correct, no_guess, buffer) = corrector.correct(x, y)
            total_wrong += wrong
            total_correct += correct
            total_no_guess += no_guess
            total_buffer.append(buffer)

        return round(total_wrong/(total_wrong+total_correct+total_no_guess)*100, 2), round(total_correct/(total_wrong+total_correct+total_no_guess)*100, 2), round(total_no_guess/(total_wrong+total_correct+total_no_guess)*100, 2), total_buffer

import time
from IPython.utils import io

tester = Tester(["FineTuneModels/models/nutidsrModel2"])

model1 = "FineTuneModels/models/nutidsrModel1"
model3 = "FineTuneModels/models/nutidsrModel3"

models = [model1, model3]
model_names = ["Model 1", "Model 3"]

for i in range(len(models)):
    start_time = time.time()
    model = models[i]
    model_name = model_names[i]

    print(model_name)
    with io.capture_output() as captured:
        wrong, correct, no_guess, scores = tester.test_one_model(load_model(model))

    print("Wrong: ", wrong)
    print("Correct: ", correct)
    print("No Guess: ", no_guess)
    print("Time: ", time.time() - start_time, "\n")
    start_time = time.time()