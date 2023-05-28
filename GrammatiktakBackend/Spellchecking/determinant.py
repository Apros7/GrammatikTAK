from Utilities.utils import prepare_sentence, find_index, move_index_based_on_br
from Utilities.error_handling import Error, ErrorList
import pickle

def find_det_noun_pairs(lst):
    indexes = []
    for i in range(len(lst)):
        if lst[i] == "DET":
            for j in range(i+1, len(lst)):
                if lst[j] == "NOUN":
                    if all(x in ["DET", "ADV", "ADJ"] for x in lst[i+1:j]):
                        indexes.append((i, j))
                    break
    return indexes

def load_dicts():
    with open("Datasets/GenderDict.pickle", "rb") as f:
        genderDict = pickle.load(f)
    with open("Datasets/SbStemDict.pickle", "rb") as f:
        sbStemDict = pickle.load(f)
    return genderDict, sbStemDict

class determinantCorrector():
    """
    Rule based detector for finding the following errors:
     - en/et
     - den/det
    """
    
    def __init__(self) -> None:
        self.genderDict, self.sbStemDict = load_dicts()
        self.posible_corrections = ["en", "et", "den", "det"]
        self.change_determinant = {"en": "et", "et": "en", "den": "det", "det": "den"}
    
    def is_determinant_fælleskøn(self, det):
        if det in ["en", "den"]:
            return True
        elif det in ["et", "det"]: 
            return False
        return None
    
    def create_determinant_error_message(self, word_to_correct, noun, all_words_from_sentence, index_of_word_in_all_words, fælleskøn) -> list:
        correct_word = self.change_determinant[word_to_correct]
        gender = "fælleskøn." if fælleskøn else "intetkøn."
        error_type = "det"
        error_description = f"Der skal skrives '{correct_word}' foran {noun}, da {noun} er {gender}"
        previous_index = find_index(all_words_from_sentence, index_of_word_in_all_words, word_to_correct)
        wrong_word = word_to_correct
        return Error(wrong_word, correct_word, previous_index, error_description, error_type)

    def correct(self, sentence, pos_tag):
        uncleaned_words = prepare_sentence(sentence)
        words = prepare_sentence(sentence, lowercase=False, clean=True)
        pos = [x[0] for x in pos_tag]
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
        return move_index_based_on_br(ErrorList(error_messages), sentence)
