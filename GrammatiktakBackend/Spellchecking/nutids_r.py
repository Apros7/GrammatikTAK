from Utilities.utils import prepare_sentence, move_index_based_on_br
from Utilities.error_handling import Error, ErrorList
from Utilities.model_utils import Dataset, load_model

import pickle
import torch
from transformers import Trainer, BertTokenizer
import numpy as np
import time
import string

model_path = "models/nutidsrModel9-BERT"
model_left_padding = 15
model_right_padding = 5
model_cutoff_value = 0.95

class NutidsRCorrector():
    def __init__(self) -> None:
        self.can_verb_be_checked = pickle.load(open("Datasets/nutids_r_stem.pickle", "rb"))
        self.get_tense_from_verb = pickle.load(open("Datasets/nutids_r_bøjninger.pickle", "rb"))
        self.tokenizer = BertTokenizer.from_pretrained("Maltehb/danish-bert-botxo")
        self.classifier = load_model(model_path)
        self.left_padding = model_left_padding
        self.right_padding = model_right_padding
        self.cutoff_value = model_cutoff_value

    def verbs_to_check(self, words, pos):
        verbs = []
        for i in range(len(pos)):
            if pos[i][0] != "VERB":                 verbs.append(False)
            elif "Tense" not in pos[i][2].keys():   verbs.append(False)
            elif pos[i][2]["Tense"] != "Pres":      verbs.append(False)
            else:                                   verbs.append(True)
        for i, bool in enumerate(verbs):
            if not bool: continue
            word = words[i].strip(",.!?():;")
            try: stemmed_verb = self.can_verb_be_checked[word]
            except: verbs[i] = False; continue
        return verbs

    def is_verbs_nutids_r(self, words, verbs_to_check):
        is_nutids_r = []
        for word, should_check in zip(words, verbs_to_check):
            word = word.strip(",.!?():;")
            if not should_check: is_nutids_r.append(None); continue
            infinitiv_form, nutids_r_form = self.get_tense_from_verb[self.can_verb_be_checked[word]]
            if word == infinitiv_form:  is_nutids_r.append(False)
            elif word == nutids_r_form: is_nutids_r.append(True)
            else: print("ERROR: word is not infinitiv or nutids_r"); is_nutids_r.append(None)
        return is_nutids_r

    def make_dataset(self, verbs_to_check, pos, words):
        pos_with_padding = ["<PAD>"]*self.left_padding + [p[0] for p in pos] + ["<PAD>"]*self.right_padding
        dataset = []
        at_indexes = []
        skipped_indexes = []
        at_index = -1

        for i, word in enumerate(words):
            if not verbs_to_check[i]: continue

            if word[-1] == "s" or pos_with_padding[i+self.left_padding] != "VERB":
                skipped_indexes.append(i); continue

            if words[i-1].lower().strip() == "og" or words[i-1][-1] == ",": 
                skipped_indexes.append(i); continue

            at_index += 1

            if words[i-1].lower().strip() == "at": 
                at_indexes.append(at_index)

            dataset.append(" ".join(pos_with_padding[i:i+self.left_padding+self.right_padding+1]))

        return dataset, at_indexes, skipped_indexes
    
    def tokenize_sentences(self, sentences):
        X_tokenized = self.tokenizer(sentences, padding=True, truncation=True)
        return X_tokenized

    def convert_dataset_to_dataloader(self, dataset):
        test_dataset = Dataset(dataset)
        return test_dataset

    def get_predictions(self, dataloader):
        raw_predictions, _, _ = self.classifier.predict(dataloader)
        scores = torch.softmax(torch.from_numpy(raw_predictions), dim=1)
        max_scores, final_prediction = torch.max(scores, dim=1)
        final_prediction = np.argmax(raw_predictions, axis=1)
        return [(p, s) for p, s in zip(final_prediction, max_scores)]
    
    def correct_at_predictions(self, predictions, at_indexes):
        true_predictions = [p for (p, s) in predictions]
        true_score = [s for (p, s) in predictions]
        for i in range(len(true_predictions)):
            if i in at_indexes:
                true_predictions[i] = 1
                true_score[i] = 1
        return list(zip(true_predictions, true_score))

    def should_verb_be_nutidsr(self, verbs_to_check, pos, words):
        dataset, at_indexes, skipped_indexes = self.make_dataset(verbs_to_check, pos, words)
        if len(dataset) < 1: return [None]*len(verbs_to_check)
        tokenized = self.tokenize_sentences(dataset)
        dataloader = self.convert_dataset_to_dataloader(tokenized)
        predictions = self.get_predictions(dataloader)
        corrected_predictions = self.correct_at_predictions(predictions, at_indexes)
        bool_predictions = list(self.turn_predictions_to_bool(corrected_predictions, verbs_to_check, skipped_indexes))
        return bool_predictions

    def turn_predictions_to_bool(self, predictions, verbs_to_check, skipped_indexes):
        prediction_index = 0
        for i in range(len(verbs_to_check)):
            if verbs_to_check[i]:
                if i in skipped_indexes: yield None; continue
                if predictions[prediction_index][1] < self.cutoff_value: yield None
                elif predictions[prediction_index][0] == 0: yield True
                else: yield False
                prediction_index += 1
            else:
                yield None

    def remove_punc(self, word):
        translator = str.maketrans('', '', string.punctuation)
        return word.translate(translator).lower()

    def get_nutidsr_comment(self, wrong, correct, to_nutids_r):
        wrong = self.remove_punc(wrong)
        correct = self.remove_punc(correct)
        if to_nutids_r:
            if correct.replace(wrong, "") == "r":
                form = "nutid"
                comment = " med nutids-r"
            else:
                form = "nutid"
                comment = ""
        else:
            if wrong.replace(correct, "") == "r":
                form = "infinitiv"
                comment = " uden nutids-r"
            else:
                form = "infinitiv"
                comment = ""
        return form, comment

    def make_nutids_r_error_message(self, word_to_correct, all_words_from_sentence, index_of_word_in_all_words, correct_word, to_nutids_r):
        if word_to_correct == correct_word: return None
        previous_index = self.index_finder.find_index(index_of_word_in_all_words, word_to_correct)
        error_type = "nutids-r"
        nutidsr_form, nutidsr_comment = self.get_nutidsr_comment(word_to_correct, correct_word, to_nutids_r)
        description = f"'{word_to_correct}' skal være bøjet i {nutidsr_form}{nutidsr_comment}, så der står '{correct_word}'."
        return Error(word_to_correct, correct_word, previous_index, description, error_type)

    def make_error_messages(self, words, should_be_nutids_r, is_nutids_r, verbs_to_check):
        errors = ErrorList()
        for i in range(len(words)):
            if len(words[i].strip(",.!?():;")) == 0:
                continue
            verb_to_check = verbs_to_check[i]
            if not verb_to_check:
                continue 
            current_word = words[i].strip(",.!?():;")
            should_be = should_be_nutids_r[i]
            is_nutid = is_nutids_r[i]
            if should_be == is_nutid or is_nutid is None or should_be is None:
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
            if error is not None:
                errors.append(error)
        return errors

    def correct(self, sentence, pos_tags, ner_tags, index_finder):
        self.index_finder = index_finder
        self.start_time = time.time()
        words = prepare_sentence(sentence, lowercase=True)
        verbs_to_check = self.verbs_to_check(words, pos_tags)
        is_nutids_r = self.is_verbs_nutids_r(words, verbs_to_check)
        should_be_nutidsr = self.should_verb_be_nutidsr(verbs_to_check, pos_tags, words)
        errors = self.make_error_messages(words, should_be_nutidsr, is_nutids_r, verbs_to_check)
        return move_index_based_on_br(errors, sentence)