from Utilities.utils import prepare_sentence, move_index_based_on_br, find_index
from Utilities.error_handling import Error, ErrorList

import pickle
import pandas as pd

"""
To do:
- Composite words
- More than one spelling mistake? Currently only corrects one spelling mistake
- Correct words but in a place where it does not make sense (jeg heder lucas)
"""

hard_coded_frequent_spelling_errors = {
    "idag": ["i dag"],
    "imorgen": ["i morgen"],
    "igår": ["i går"],
    "igang": ["i gang"],
}

NO_CORRECTION_IF_IN_WORD = "-_"
PARTLY_CLEANING = ",.:;?!()[]{}'\""

class SpellChecker():
    def __init__(self) -> None:
        print("Loading spellchecking dictionaries...")
        self.dictionary = pickle.load(open("Datasets/dictionary.pickle", "rb"))
        self.spelling_errors = {**hard_coded_frequent_spelling_errors, **pickle.load(open("Datasets/misspellings_dict.pickle", "rb"))}

    def is_word_in_dictionary(self, word): return not word in self.dictionary
    def punctuation_in_word(self, word): return any([x in word for x in NO_CORRECTION_IF_IN_WORD])
    def partly_clean_sentence(self, sent): return ''.join(char for char in sent if char not in PARTLY_CLEANING)
    def has_possible_correct(self, word): return word in self.spelling_errors

    def create_error_message(self, wrong_word, correct_word, all_words_from_sentence, index_of_word_in_all_words) -> list:
        error_type = "spellcheck"
        correct_word = correct_word[0] if len(correct_word) == 1 else correct_word
        error_description = f"{wrong_word} er ikke ordbogen. Mente du en af disse ord?" if isinstance(correct_word, list) else f"{wrong_word} er ikke ordbogen. Mente du '{correct_word}'?"
        previous_index = find_index(all_words_from_sentence, index_of_word_in_all_words, wrong_word)
        return Error(wrong_word, correct_word, previous_index, error_description, error_type)
    
    def correct_word(self, word, index, words):
        if self.punctuation_in_word(word): return None
        if not self.is_word_in_dictionary(word): return None
        if not self.has_possible_correct(word): return None
        return self.create_error_message(word, self.spelling_errors[word], words, index)

    def correct(self, input):
        words = prepare_sentence(input)
        cleaned_words = prepare_sentence(self.partly_clean_sentence(input), lowercase=True)
        errors = ErrorList([self.correct_word(word, index, words) for index, word in enumerate(cleaned_words)])
        return errors

