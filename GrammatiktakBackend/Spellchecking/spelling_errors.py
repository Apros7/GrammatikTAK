from Utilities.error_handling import Error, ErrorList
from Utilities import utils

import pickle
import pandas as pd

# Currently below does not allow for any corrections. Maybe is hould in the composite words correction?
NO_CORRECTION_IF_IN_WORD = "-_/"
PARTLY_CLEANING = ",.:;?!()[]{}'\""
METERS_PREFIX = ["nano", "micro", "milli", "", "deci", "kilo", "mega", "giga", "tera", "peta", "exa", "zetta", "yotta"]

## NEEDS REWORK - SLOW AND BAD ##
def load_spelling_errors(): # Faster to load keys and values seperately than the complete dictionary with pickle.
    return {}
    #return {k: v for k,v in zip(pickle.load(open("Datasets/spelling_errors_keys.pickle", "rb")), pickle.load(open("Datasets/spelling_errors_values.pickle", "rb")))}

class SpellChecker():

    """
    Built using the Misspeller class based on research on danish misspellings.
    To improve the spelling_errors dict, improve the misspeller class
    """

    def __init__(self) -> None:
        print("Loading spellchecking dictionaries...")
        self.dictionary = pickle.load(open("Datasets/dictionary.pickle", "rb"))
        self.spelling_errors = load_spelling_errors()
        self.meter_errors = {k: v for k, v in zip([prefix + "met" for prefix in METERS_PREFIX], [prefix + "meter" for prefix in METERS_PREFIX])}
        self.verbs_ending_dict = pickle.load(open("Datasets/verb_ending_dict.pickle", "rb"))
        self.sb_ending_dict = pickle.load(open("Datasets/sb_ending_dict.pickle", "rb"))

    def is_word_in_dictionary(self, word): return word in self.dictionary
    def punctuation_in_word(self, word): return any([x in word for x in NO_CORRECTION_IF_IN_WORD])
    def partly_clean_sentence(self, sent): return ''.join(char for char in sent if char not in PARTLY_CLEANING)
    def has_possible_misspelling_correction(self, word): return word in self.spelling_errors
    def word_in_ner_tags(self, word_index, ner_tags): return any([word_index == ner_index for ner_index in ner_tags])

    def create_spellchecking_error_message(self, wrong_word, correct_word, index_of_word_in_all_words) -> list:
        error_type = "spellcheck"
        ## When frontend can take lists change this:
        correct_word = correct_word[0] if len(correct_word) == 1 else correct_word
        error_description = f"{wrong_word} er ikke ordbogen. Mente du en af disse ord?" if isinstance(correct_word, list) else f"{wrong_word} er ikke ordbogen. Mente du '{correct_word}'?"
        previous_index = self.index_finder.find_index(index_of_word_in_all_words, wrong_word)
        return Error(wrong_word, correct_word, previous_index, error_description, error_type)
    
    def correct_spelling_mistake(self, word, index, ner_tags):
        if self.punctuation_in_word(word): return None
        if self.is_word_in_dictionary(word): return None
        if self.word_in_ner_tags(index, ner_tags): return None
        if word in self.meter_errors: return self.create_spellchecking_error_message(word, self.meter_errors[word], index)
        if not self.has_possible_misspelling_correction(word): return None
        return self.create_spellchecking_error_message(word, self.spelling_errors[word], index)

    def correct_ending_mistake(self, word, index):
        print(word, word in self.verbs_ending_dict, word in self.sb_ending_dict)
        if word in self.verbs_ending_dict: return self.create_spellchecking_error_message(word, self.verbs_ending_dict[word], index)
        if word in self.sb_ending_dict: return self.create_spellchecking_error_message(word, self.sb_ending_dict[word], index)
        print("Retuning none")
        return None

    def correct(self, sentence, pos_tags, ner_tags, index_finder):
        self.index_finder = index_finder
        cleaned_words = utils.prepare_sentence(self.partly_clean_sentence(sentence), lowercase=True)
        spelling_errors = ErrorList([self.correct_spelling_mistake(word, index, ner_tags) for index, word in enumerate(cleaned_words)])
        ending_errors = ErrorList([self.correct_ending_mistake(word, index) for index, word in enumerate(cleaned_words)])
        return utils.move_index_based_on_br(spelling_errors + ending_errors, sentence)