from Utilities.utils import prepare_sentence, move_index_based_on_br
from Utilities.error_handling import Error, ErrorList

import pickle
import pandas as pd

# Currently below does not allow for any corrections. Maybe is hould in the composite words correction?
NO_CORRECTION_IF_IN_WORD = "-_/"
PARTLY_CLEANING = ",.:;?!()[]{}'\""
METERS_PREFIX = ["nano", "micro", "milli", "", "deci", "kilo", "mega", "giga", "tera", "peta", "exa", "zetta", "yotta"]

def load_spelling_errors(): # Faster to load keys and values seperately than the complete dictionary with pickle.
    return {k: v for k,v in zip(pickle.load(open("Datasets/spelling_errors_keys.pickle", "rb")), pickle.load(open("Datasets/spelling_errors_values.pickle", "rb")))}

class SpellChecker():

    """
    Built using the Misspeller class based on research on danish misspellings.
    To improve the spelling_errors dict, improve the misspeller class
    """

    def __init__(self) -> None:
        print("Loading spellchecking dictionaries...")
        self.composite_words = pickle.load(open("Datasets/composite_words.pickle", "rb"))
        self.dictionary = pickle.load(open("Datasets/dictionary.pickle", "rb"))
        self.spelling_errors = load_spelling_errors()
        self.meter_errors = {k: v for k, v in zip([prefix + "met" for prefix in METERS_PREFIX], [prefix + "meter" for prefix in METERS_PREFIX])}
        print(self.composite_words[:10])

    def is_word_in_dictionary(self, word): return word in self.dictionary
    def punctuation_in_word(self, word): return any([x in word for x in NO_CORRECTION_IF_IN_WORD])
    def partly_clean_sentence(self, sent): return ''.join(char for char in sent if char not in PARTLY_CLEANING)
    def has_possible_misspelling_correction(self, word): return word in self.spelling_errors
    def word_in_ner_tags(self, word, ner_tags): return any([word in ner[0].lower() for ner in ner_tags]) # Should probably be changed

    def get_composite_combinations(self, word): 
        return [word[:i] + word[i+1:] for i in range(len(word)) if word[i] == " "] + [word[:i] + " " + word[i:] for i in range(len(word))]

    def composite_words_error(self, word): 
        for composite_word in self.get_composite_combinations(word): 
            if composite_word in self.composite_words: return (True, composite_word)
        return (False, None)

    def create_spellchecking_error_message(self, wrong_word, correct_word, all_words_from_sentence, index_of_word_in_all_words) -> list:
        error_type = "spellcheck"
        ## When frontend can take lists change this:
        correct_word = correct_word[0] if len(correct_word) == 1 else correct_word
        error_description = f"{wrong_word} er ikke ordbogen. Mente du en af disse ord?" if isinstance(correct_word, list) else f"{wrong_word} er ikke ordbogen. Mente du '{correct_word}'?"
        previous_index = self.index_finder.find_index(all_words_from_sentence, index_of_word_in_all_words, wrong_word)
        return Error(wrong_word, correct_word, previous_index, error_description, error_type)
    
    def correct_spelling_mistakes(self, word, index, words, ner_tags):
        if self.punctuation_in_word(word): return None
        if self.is_word_in_dictionary(word): return None
        if self.word_in_ner_tags(word, ner_tags): return None
        if word in self.meter_errors: return self.create_spellchecking_error_message(word, self.meter_errors[word], words, index)
        if not self.has_possible_misspelling_correction(word): return None
        return self.create_spellchecking_error_message(word, self.spelling_errors[word], words, index)

    def correct(self, sentence, pos_tags, ner_tags, index_finder):
        self.index_finder = index_finder
        words = prepare_sentence(sentence)
        cleaned_words = prepare_sentence(self.partly_clean_sentence(sentence), lowercase=True)
        spelling_errors = ErrorList([self.correct_spelling_mistakes(word, index, words, ner_tags) for index, word in enumerate(cleaned_words)])
        return move_index_based_on_br(spelling_errors, sentence)