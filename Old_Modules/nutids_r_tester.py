from Spellchecking.nutids_r import NutidsRCorrector

import pandas as pd
from Helpers.tagger import Tagger
import pickle
from tqdm import tqdm
import time

# # BEFORE RUNNING CHANGE RETURN STATEMENT IN PREDICTION TO:
# return move_index_based_on_br(errors, sentence), verbs_to_check, self.buffer, self.edge_cases, should_be_nutids_r

start_time = time.time()

class NutidsRTester():
    def __init__(self, corrector: NutidsRCorrector):
        self.corrector = corrector
        self.x, self.y = self.get_testset()
    
    def get_testset(self):
        df = pd.read_csv("Datasets/EuroparlNutidsr_testset.csv", sep=";")

        size = 1000
        x = df["wrong"][:size]
        y = df["correct"][:size]
        # x = [df["wrong"][i] for i in [51, 57, 65]]
        # y = [df["correct"][i] for i in [51, 57, 65]]
        return x,y

    def predict(self):
        predictions = []
        with open("pos_caching.pkl", "rb") as f:
            pos_list = pickle.load(f)
        print(len(pos_list), len(self.x))
        if len(pos_list) != len(self.x):
            pos_list = []
            tagger = Tagger()
            for sentence in tqdm(self.x):
                pos, ner = tagger.get_tags(sentence)
                pos_list.append(pos)
            print(len(pos_list))
            print("Updating")
            with open("pos_caching.pkl", "wb") as f:
                pickle.dump(pos_list, f)
            print("Updated")
        else:
            print("pos_caching.pkl already exists")
        
        for i in tqdm(range(len(self.x))):
            sentence = self.x[i]
            pos = pos_list[i]
            errors, verbs_to_check, buffer, edge_cases, should_be_nutids_r, pos = self.corrector.correct(sentence, pos)
            for error in errors:
                sentence = sentence[:error[2][0]] + error[1] + sentence[error[2][1]:]
                diff = len(error[1]) - len(error[0])
                for error in errors:
                    error[2] = (error[2][0] + diff, error[2][1] + diff)
            predictions.append((sentence, verbs_to_check, errors, buffer, edge_cases, should_be_nutids_r, pos))
        return predictions

    def get_measurements(self, predictions):
        correct = 0
        no_guess = 0
        wrong = 0

        for x in range(len(self.y)):
            actual = self.y[x]
            (prediction, verbs_to_check, errors, buffer, (edge_cases, edge_cases_concat, sbj_adv_ignored), should_be_nutids, pos) = predictions[x]

            actual = actual.strip()
            actual_words = actual.split()
            predition_words = prediction.split()
            should_print = False
            should_be_where_wrong = []
            edge_where_wrong = []
            wrong_words = []

            for i in range(len(actual_words)):
                actual_word = actual_words[i]
                prediction_word = predition_words[i]
                if actual_word != prediction_word:
                    if verbs_to_check[i] and should_be_nutids[i] is not None:
                        wrong_words.append(actual_word)
                        wrong += 1
                        should_print = True
                        should_be_where_wrong.append(should_be_nutids[i])
                        edge_where_wrong.append([edge_cases[x][i] for x in range(len(edge_cases))])
                    else:
                        no_guess += 1
                else: 
                    if verbs_to_check[i]:
                        correct += 1

            if actual == prediction:
                continue

            if should_print:
                print(x)
                print(actual)
                print(prediction)
                print(*errors, sep="\n")
                print("Wrong words:", wrong_words)
                print("\n")
                print("Edge cases: ", *edge_where_wrong, sep="\n")
                print("Should be: ", should_be_where_wrong)
                print("\n")
                print("Verbs to check: ", verbs_to_check)
                print("\n")
                print("Ignore ADV and SBJ: ", sbj_adv_ignored)
                print("\n")
                print("Buffer: ", buffer)
                print("\n")
                print("POS: ", pos)
                print("\n")

        self.print_measurements(correct, no_guess, wrong, correct+no_guess+wrong)

    def print_measurements(self, correct, no_guess, wrong, len_of_testset):
        print(f"Percentage of correct: {correct}/{len_of_testset} = {round(correct/len_of_testset*100, 4)}%")
        print(f"Percentage of no guess: {no_guess}/{len_of_testset} = {round(no_guess/len_of_testset*100, 4)}%")
        print(f"Percentage of wrong: {wrong}/{len_of_testset} = {round(wrong/len_of_testset*100, 4)}%")
        print(f"Time taking: {round(time.time() - start_time, 4)} seconds")

    def test(self):
        predictions = self.predict()
        self.get_measurements(predictions)

corrector = NutidsRCorrector()
nutids_r_tester = NutidsRTester(corrector)
nutids_r_tester.test()

## 88% correct
## 6% guess
## 6% wrong
