from Utilities.utils import prepare_sentence, find_index, move_index_based_on_br
from Utilities.error_handling import Error, ErrorList
import pickle

def find_det_noun_pairs(lst, only_adj=False):
    indexes = []
    for i in range(len(lst)):
        if lst[i] == "DET":
            for j in range(i+1, len(lst)):
                if lst[j] == "NOUN":
                    if only_adj:
                        if all(x in ["ADJ"] for x in lst[i+1:j]):
                            indexes.append((i, j))
                    else:
                        if all(x in ["DET", "ADV", "ADJ"] for x in lst[i+1:j]):
                            indexes.append((i, j))
                    break
    return indexes

class DeterminantCorrector():
    """
    Rule based detector for finding the following errors:
     - en/et
     - den/det
     - if adjective should end on "t": et stor hus vs et stort hus
    """
    def __init__(self) -> None:
        self.genderDict = pickle.load(open("Datasets/GenderDict.pickle", "rb"))
        self.sbStemDict = pickle.load(open("Datasets/SbStemDict.pickle", "rb"))
        self.adjectiveList = pickle.load(open("Datasets/AdjectiveList.pickle", "rb"))
        self.posible_corrections = ["en", "et", "den", "det"]
        self.change_determinant = {"en": "et", "et": "en", "den": "det", "det": "den"}

    def is_adjective_fælleskøn(self, adjective): return False if adjective[-1] == "t" else True
    
    def is_determinant_fælleskøn(self, determinant):
        if determinant in ["en", "den"]: return True
        elif determinant in ["et", "det"]: return False
        return None

    def create_adjective_error_message(self, word_to_correct, noun, all_words_from_sentence, index_of_word_in_all_words, fælleskøn):
        correct_word = word_to_correct[:-1] if fælleskøn else word_to_correct + "t"
        gender = "fælleskøn." if fælleskøn else "intetkøn."
        error_type = "det"
        error_description = f"{word_to_correct} ser ikke ud til at være bøjet korrekt. Der skal skrives '{correct_word}' foran {noun}, da {noun} er {gender}"
        previous_index = find_index(all_words_from_sentence, index_of_word_in_all_words, word_to_correct)
        wrong_word = word_to_correct
        return Error(wrong_word, correct_word, previous_index, error_description, error_type)
    
    def create_determinant_error_message(self, word_to_correct, noun, all_words_from_sentence, index_of_word_in_all_words, fælleskøn):
        correct_word = self.change_determinant[word_to_correct]
        gender = "fælleskøn." if fælleskøn else "intetkøn."
        error_type = "det"
        error_description = f"Der skal skrives '{correct_word}' foran {noun}, da {noun} er {gender}"
        previous_index = find_index(all_words_from_sentence, index_of_word_in_all_words, word_to_correct)
        wrong_word = word_to_correct
        return Error(wrong_word, correct_word, previous_index, error_description, error_type)

    def correct_adjective(self, words, pos):
        indexes = find_det_noun_pairs(pos, only_adj=True)
        error_messages = []
        for pair in indexes:
            print(pair, pair[1] - pair[0])
            if pair[1] - pair[0] != 2: continue
            is_fællesskøn = self.is_adjective_fælleskøn(words[pair[0]+1])
            print(is_fællesskøn)
            noun = words[pair[1]].lower()
            adjective = words[pair[0] + 1].lower()
            word_to_check = adjective if is_fællesskøn else adjective[:-1]
            print(word_to_check, word_to_check in self.adjectiveList)
            if not word_to_check in self.adjectiveList: continue
            print("hey")
            try: should_be_fælleskøn = self.genderDict[self.sbStemDict[noun]]
            except: continue
            print("hey")
            print(should_be_fælleskøn, is_fællesskøn)
            if should_be_fælleskøn != is_fællesskøn:
                error_messages.append(self.create_adjective_error_message(adjective, noun, words, pair[0]+1, should_be_fælleskøn))
        return error_messages

    def correct_determinant(self, words, uncleaned_words, pos):
        indexes = find_det_noun_pairs(pos)
        error_messages = []
        for pair in indexes:
            det = words[pair[0]].lower()
            noun = words[pair[1]].lower()
            is_fælleskøn = self.is_determinant_fælleskøn(det)
            if is_fælleskøn is None: continue
            try: should_be_fælleskøn = self.genderDict[self.sbStemDict[noun]]
            except: continue
            if should_be_fælleskøn != is_fælleskøn:
                error_messages.append(self.create_determinant_error_message(det, noun, uncleaned_words, pair[0], should_be_fælleskøn))
        return error_messages

    def correct(self, sentence, pos_tag, ner_tags):
        uncleaned_words = prepare_sentence(sentence)
        words = prepare_sentence(sentence, lowercase=False, clean=True)
        pos = [x[0] for x in pos_tag]
        adjective_errors = self.correct_adjective(words, pos)
        determinant_errors = self.correct_determinant(words, uncleaned_words, pos)
        return move_index_based_on_br(ErrorList(determinant_errors + adjective_errors), sentence)
    