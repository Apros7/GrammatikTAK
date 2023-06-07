from Utilities.utils import prepare_sentence, move_index_based_on_br, find_index
from Utilities.error_handling import Error, ErrorList

import pickle
import pandas as pd


NO_CORRECTION_IF_IN_WORD = "-_"
PARTLY_CLEANING = ",.:;?!()[]{}'\""

def load_spelling_errors(): # Faster to load keys and values seperately than the complete dictionary with pickle.
    return {k: v for k,v in zip(pickle.load(open("Datasets/spelling_errors_keys.pickle", "rb")), pickle.load(open("Datasets/spelling_errors_values.pickle", "rb")))}

class SpellChecker():

    """
    Built using the Misspeller class based on research on danish misspellings.
    """

    def __init__(self) -> None:
        print("Loading spellchecking dictionaries...")
        self.composite_words = pickle.load(open("Datasets/composite_words.pickle", "rb"))
        self.dictionary = pickle.load(open("Datasets/dictionary.pickle", "rb"))
        self.spelling_errors = load_spelling_errors()

    def is_word_in_dictionary(self, word): return word in self.dictionary
    def punctuation_in_word(self, word): return any([x in word for x in NO_CORRECTION_IF_IN_WORD])
    def partly_clean_sentence(self, sent): return ''.join(char for char in sent if char not in PARTLY_CLEANING)
    def has_possible_misspelling_correction(self, word): return word in self.spelling_errors

    def get_composite_combinations(self, word): 
        return [word[:i] + word[i+1:] for i in range(len(word)) if word[i] == " "] + [word[:i] + " " + word[i:] for i in range(len(word))]

    def composite_words_error(self, word): 
        for composite_word in self.get_composite_combinations(word): 
            if composite_word in self.composite_words: return (True, composite_word)
        return (False, None)

    def create_error_message(self, wrong_word, correct_word, all_words_from_sentence, index_of_word_in_all_words) -> list:
        error_type = "spellcheck"
        correct_word = correct_word[0] if len(correct_word) == 1 else correct_word
        error_description = f"{wrong_word} er ikke ordbogen. Mente du en af disse ord?" if isinstance(correct_word, list) else f"{wrong_word} er ikke ordbogen. Mente du '{correct_word}'?"
        previous_index = find_index(all_words_from_sentence, index_of_word_in_all_words, wrong_word)
        return Error(wrong_word, correct_word, previous_index, error_description, error_type)
    
    def correct_word(self, word, index, words):
        if self.punctuation_in_word(word): return None
        if self.is_word_in_dictionary(word): return None
        is_composite_error, composite_word = self.composite_words_error(word)
        if is_composite_error: return self.create_error_message(word, composite_word, words, index)
        if not self.has_possible_misspelling_correction(word): return None
        return self.create_error_message(word, self.spelling_errors[word], words, index)

    def correct(self, input, pos_tags, ner_tags):
        words = prepare_sentence(input)
        cleaned_words = prepare_sentence(self.partly_clean_sentence(input), lowercase=True)
        errors = ErrorList([self.correct_word(word, index, words) for index, word in enumerate(cleaned_words)])
        return errors