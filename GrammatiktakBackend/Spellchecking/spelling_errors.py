import sys
sys.path.append("/Users/lucasvilsen/Desktop/GrammatikTAK/GrammatiktakBackend/")
from Utilities.error_handling import Error, ErrorList
from Utilities import utils

import translators as ts
import pickle
import time
import pandas as pd
import string
import os
from tqdm import tqdm
import difflib
import emoji

# Currently below does not allow for any corrections. Maybe is hould in the composite words correction?
NO_CORRECTION_IF_IN_WORD = "-_/'\"”"
PARTLY_CLEANING = ",:;?!()[]{}'\""
METERS_PREFIX = ["nano", "micro", "milli", "", "deci", "kilo", "mega", "giga", "tera", "peta", "exa", "zetta", "yotta"]

class SpellChecker():

    """
    Corrects endings, meters error by itself
    Corrects spelling errors using SpellingWizard
    """
    
    def __init__(self) -> None:
        print("Loading spellchecking dictionaries...")
        # Also needs forkortelser in dictionary
        self.dictionary = {k: None for k in pickle.load(open("Datasets/dictionary.pickle", "rb"))}
        self.dictionary.update({k: None for k in pickle.load(open("Datasets/additional_dictionary.pickle", "rb"))})
        self.abbreviations = pickle.load(open("Datasets/abbreviations_dict.pickle", "rb"))
        self.meter_errors = {k: v for k, v in zip([prefix + "met" for prefix in METERS_PREFIX], [prefix + "meter" for prefix in METERS_PREFIX])}
        self.verbs_ending_dict = pickle.load(open("Datasets/verb_ending_dict.pickle", "rb"))
        self.sb_ending_dict = pickle.load(open("Datasets/sb_ending_dict.pickle", "rb"))
        self.spelling_wizard = SpellingWizard()
        self.translation = None

    def relative_words_alike_score(self, word1, word2): return (difflib.SequenceMatcher(None, word1, word2).ratio() * 100) / len(word1)
    def is_word_in_dictionary(self, word): return word.replace(".", "") in self.dictionary
    def punctuation_in_word(self, word): return any([x in word for x in NO_CORRECTION_IF_IN_WORD])
    def partly_clean_sentence(self, sent): return ''.join(char for char in sent if char not in PARTLY_CLEANING)
    def partly_clean_words(self, words): return [word.translate(str.maketrans('', '', PARTLY_CLEANING)) for word in words]
    def word_in_ner_tags(self, word_index, ner_tags): return any([word_index == ner_index for ner_index in ner_tags])
    def emoji_in_word(self, word): return word != emoji.demojize(word)

    def get_translation(self, words): 
        if not self.translation:
            print("Translating...")
            to_english = ts.translate_text(" ".join(words), translator="google", from_language='da', to_language='en')
            translation = ts.translate_text(to_english, translator='google', from_language='en', to_language='da').split()
            self.translation = self.partly_clean_words(translation)

    def find_translation(self, words, index):
        self.get_translation(words)
        phrase = words[max(index-1, 0):index+2]
        if len(phrase) != 3: return None
        is_upper = words[index][0].isupper()
        for i in range(-5, 5):
            translation_phrase = self.translation[index-1+i:index+2+i]
            if len(translation_phrase) != 3: continue
            to_return = translation_phrase[1].capitalize() if is_upper else translation_phrase[1].lower()
            if phrase[0] != translation_phrase[0] or phrase[2] != translation_phrase[2]: continue
            if self.relative_words_alike_score(phrase[1], to_return) < 20: return to_return
        return None

    def create_spellchecking_error_message(self, wrong_word, correct_word, index_of_word_in_all_words, abbreviation=False, translation=False) -> list:
        error_type = "spellcheck"
        ## When frontend can take lists change this:
        correct_word = correct_word[0] if type(correct_word) == list else correct_word
        if abbreviation: error_description = f"Det ligner, at du har skrevet forkotelsen '{wrong_word}' forkert. Den rigtige måde er: '{correct_word}'."
        elif translation: error_description = f"Det ligner, at du har skrevet et engelsk ord '{wrong_word}'. Du kunne overveje at oversætte dette til dansk: '{correct_word}'."
        else: error_description = f"{wrong_word} er ikke ordbogen. Mente du en af disse ord?" if isinstance(correct_word, list) else f"{wrong_word} er ikke ordbogen. Mente du '{correct_word}'?"
        previous_index = self.index_finder.find_index(index_of_word_in_all_words, wrong_word)
        return Error(wrong_word, correct_word, previous_index, error_description, error_type)
    
    def correct_spelling_mistake(self, word, index, ner_tags, words):
        if self.punctuation_in_word(word) or self.emoji_in_word(word): return None
        if self.is_word_in_dictionary(word) or self.word_in_ner_tags(index, ner_tags): return None
        if word in self.meter_errors: return self.create_spellchecking_error_message(word, self.meter_errors[word], index)
        if word.replace(".", "") in self.abbreviations: return None if word == self.abbreviations[word.replace(".", "")] else self.create_spellchecking_error_message(word, self.abbreviations[word.replace(".", "")], index, abbreviation=True)
        # print("Translating because of:", word)
        # TRANSLATION DOES NOT WORK
        # translation_return = self.find_translation(words, index)
        # print(translation_return, translation_return in self.dictionary)
        # if translation_return and translation_return in self.dictionary: return self.create_spellchecking_error_message(word, translation_return, index, translation=True)
        wizard_return = self.spelling_wizard.correct(word)
        if wizard_return: return self.create_spellchecking_error_message(word, wizard_return, index)
        return None

    def correct_ending_mistake(self, word, index):
        if word in self.verbs_ending_dict: return self.create_spellchecking_error_message(word, self.verbs_ending_dict[word], index)
        if word in self.sb_ending_dict: return self.create_spellchecking_error_message(word, self.sb_ending_dict[word], index)
        return None

    def correct(self, sentence, pos_tags, ner_tags, index_finder):
        self.translation = None
        self.index_finder = index_finder
        cleaned_words = utils.prepare_sentence(self.partly_clean_sentence(sentence), lowercase=True)
        spelling_errors = ErrorList([self.correct_spelling_mistake(word, index, ner_tags, cleaned_words) for index, word in enumerate(cleaned_words)])
        ending_errors = ErrorList([self.correct_ending_mistake(word, index) for index, word in enumerate(cleaned_words)])
        return utils.move_index_based_on_br(spelling_errors + ending_errors, sentence)

lowercase_letters = list(string.ascii_lowercase)
uppercase_letters = list(string.ascii_uppercase)

vocals = ["a", "e", "i", "o", "u", "y", "æ", "ø", "å"]
consonant = ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'v', 'w', 'x', 'z']

class SpellingWizard():

    """
    Tries to find the correct word given a misspelled word (not in dictionary).
    Based on research on danish misspellings.

    this is build of the following report (p. 26-) (mainly from p. 38-): 
    https://dsn.dk/wp-content/uploads/2021/01/Saadan.staver.vi_.pdf
    """

    def __init__(self) -> None:
        self.permutations = []
        self.dictionary = {k: None for k in pickle.load(open("Datasets/dictionary.pickle", "rb"))}

    def reverse_dict(self, dict): return {v: k for k, v in dict.items()}
    def reset(self): self.permutations = []
    def permutations_in_dictionary(self): return list(set([permutation for permutation in self.permutations if permutation in self.dictionary]))

    def _permutate_single(self, dict):
        for i, letter in enumerate(self.word):
            if letter in dict.keys():
                if type(dict[letter]) == str:
                    permutation = list(self.word)
                    permutation[i] = dict[letter]
                    self.permutations.append("".join(permutation))
                else:
                    for option in dict[letter]:
                        permutation = list(self.word)
                        permutation[i] = option
                        self.permutations.append("".join(permutation))

    def _permutate_double(self, dict):
        for i in range(len(self.word)-1):
            if self.word[i:i+2] in dict.keys():
                permutation = list(self.word)
                permutation[i] = dict[self.word[i:i+2]]
                permutation[i+1] = ""
                self.permutations.append("".join(permutation))

    def permutate(self, dict):
        len_to_permutatation_dict = {1: self._permutate_single, 2: self._permutate_double}
        len_to_permutatation_dict[len(list(dict.keys())[0])](dict)
        if list in [type(value) for value in dict.values()]:
            return # Not doing reverseDict as list in values
        reverseDict = self.reverse_dict(dict)
        len_to_permutatation_dict[len(list(reverseDict.keys())[0])](reverseDict)

    def missing_s(self):
        for i, letter in enumerate(self.word): self.permutations.append(self.word[:i] + self.word[i+1:]) if letter == "s" else None
        for i, letter in enumerate(self.word): self.permutations.append(self.word[:i] + "s" + self.word[i:])
    
    def other_silent(self):
        silent_letters = ["g", "t", "v"]
        for i in range(len(self.word) + 1):
            for letter in silent_letters:
                new_word = self.word[:i] + letter + self.word[i:]
                self.permutations.append(new_word)
        for i in range(len(self.word)):
            for letter in silent_letters:
                if self.word[i] == letter:
                    self.permutations.append(self.word[:i] + self.word[i+1:])

    def get_permutations(self): 
        for dict in self.dicts(): self.permutate(dict)
        self.missing_s(); self.other_silent()

    def dicts(self):
        double_const_dict = {const: 2*const for const in lowercase_letters}
        single_letter_confusion = {"b": "p", "d": ["t", "g", "j"], "g": ["k", "j", "v"], "f": "v", "k": "t", "c": "s", "i": "j"}
        reverse_single_letter = {"p": "b", "v": ["g", "f"], "s": "c", "t": ["d", "k"], "g": "d", "j": ["d", "g", "j"], "k": "g"}
        double_letter_confusion = {"bb":"pp", "dd":"tt", "gg":"kk", "ld":"ll", "nd":"nn", "rd":"rr", "ds":"ss", "dt":"tt"}
        silent_d_dict = {"ld": "l", "nd": "n", "rd": "r"}
        missing_h_dict = {"hj": "j", "hv": "v"}
        silent_letters_dict = {"nt":"n", "st": "s", "et": "e", "lv": "l", "vt": "v"}
        wrong_vocal_dict = {"a": ["æ", "e"], "e": ["æ", "i"], "o": "u", "ø": "y", "æ": "i", "å": ["u", "o"]}
        reverse_wrong_vocal_dict = {"e": "a", "i": ["æ", "e"], "u": ["å", "o"], "y": "ø", "o": "å", "æ": ["a", "e"]}
        return [double_const_dict, single_letter_confusion, reverse_single_letter, double_letter_confusion, silent_d_dict,
                missing_h_dict, silent_letters_dict, wrong_vocal_dict, reverse_wrong_vocal_dict]

    def correct(self, word):
        self.reset()
        self.word = word
        self.get_permutations()
        result = self.permutations_in_dictionary()
        if len(result) == 0:
            permutations_to_check = self.permutations
            self.reset()
            for word in permutations_to_check:
                self.word = word
                self.get_permutations()
            result = self.permutations_in_dictionary()
        return None if len(result) < 1 else result

if __name__ == "__main__":
    wizard = SpellingWizard()
    os.chdir("/Users/lucasvilsen/Desktop/GrammatiktakDatasets")
    df = pd.read_csv("Danish/spelling_errors.csv", encoding="UTF-8", sep="|")
    wrong = df["wrong"]
    right1 = df["right1"]
    right2 = df["right2"]
    nones = 0
    rights = 0
    wrongs = 0
    fucked = 0
    for w, r1, r2 in tqdm(zip(wrong, right1, right2)):
        result = wizard.correct(w)
        if result is None: nones += 1
        elif r1 in result or r2 in result: rights += 1
        elif r1 not in wizard.dictionary or w == r1: fucked += 1
        else: wrongs += 1; print((w, r1, r2, result))
    print("nones:", nones, "\nrights:", rights, "\nwrongs:", wrongs, "\nfucked:", fucked)

    # Best results so far:
    # correct: 265
    # wrong: 40
    # nones: 239