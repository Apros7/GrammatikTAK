import string
import os
import numpy as np
import pandas as pd
from tqdm import tqdm

lowercase_letters = list(string.ascii_lowercase)
uppercase_letters = list(string.ascii_uppercase)

vocals = ["a", "e", "i", "o", "u", "y", "æ", "ø", "å"]
consonant = ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'v', 'w', 'x', 'z']

WordToKeybordMapping: dict[str, tuple] = {
    "z": (1,1), "x": (1,2), "c": (1,3), "v": (1,4), "b": (1,5), "n": (1,6), "m": (1,7),
    "a": (2,1), "s": (2,2), "d": (2,3), "f": (2,4), "g": (2,5), "h": (2,6), "j": (2,7), 
    "k": (2,8), "l": (2,9),"æ": (2, 10), "ø": (2, 11), "q": (3, 1), "w": (3, 2), "e": (3, 3),
    "r": (3, 4), "t": (3, 5), "y": (3, 6), "u": (3, 7),  "i": (3, 8), "o": (3, 9), "p": (3, 10), "å": (3, 11)
}

KeyboardToWordMapping: dict[tuple, str] = {v: k for k, v in WordToKeybordMapping.items()}

def reverse_dict(dict):
    return {v: k for k, v in dict.items()}

NO_CORRECTION_IF_IN_WORD = "'-_.,;:!?()[]{}"

class Misspeller():

    """
    Used to create credible misspellings in correct sentences

    this is build of the following report (p. 26-) (mainly from p. 38-): 
    https://dsn.dk/wp-content/uploads/2021/01/Saadan.staver.vi_.pdf

    """

    def __init__(self, debug = False):
        self.permutations = []
        self.debug = debug

    def get_keyboard_adjacent_letters(self, letter):
        if letter not in WordToKeybordMapping.keys():
            return [None]
        keyboard_coordinates = WordToKeybordMapping[letter]
        adjacent_coordinates = [(keyboard_coordinates[0] - 1, keyboard_coordinates[1]), (keyboard_coordinates[0] + 1, keyboard_coordinates[1]),
                            (keyboard_coordinates[0], keyboard_coordinates[1] - 1), (keyboard_coordinates[0], keyboard_coordinates[1] + 1)]
        adjacent_letters = []
        for i in range(len(adjacent_coordinates)):
            try:
                word = KeyboardToWordMapping[adjacent_coordinates[i]]
                adjacent_letters.append(word)
            except KeyError:
                adjacent_letters.append(None)
        return adjacent_letters
    
    def get_keyboard_adjacent_for_word(self, word):
        result = {}
        for letter in word:
            adjacent_letters = self.get_keyboard_adjacent_letters(letter)
            result[letter] = adjacent_letters
        return result

    def _permutate_single(self, word, dict):
        for i, letter in enumerate(word):
            if letter in dict.keys():
                if type(dict[letter]) == str:
                    permutation = list(word)
                    permutation[i] = dict[letter]
                    self.permutations.append("".join(permutation))
                else:
                    for option in dict[letter]:
                        permutation = list(word)
                        permutation[i] = option
                        self.permutations.append("".join(permutation))

    def _permutate_double(self, word, dict):
        for i in range(len(word)-1):
            if word[i:i+2] in dict.keys():
                permutation = list(word)
                permutation[i] = dict[word[i:i+2]]
                permutation[i+1] = ""
                self.permutations.append("".join(permutation))

    def permutate(self, word, dict, reverseDict):
        debug1 = self.permutations
        len_to_permutatation_dict = {1: self._permutate_single, 2: self._permutate_double}
        len_to_permutatation_dict[len(list(dict.keys())[0])](word, dict)
        debug2 = self.permutations
        len_to_permutatation_dict[len(list(reverseDict.keys())[0])](word, reverseDict)
        debug3 = self.permutations

        if self.debug: 
            print(debug1)
            print(debug2)
            print(debug3)

    def keyboard_mistakes(self, word):
        # currently not used (due to exessive, mostly useless complexity)
        keyboard_letter_mistakes = self.get_keyboard_adjacent_for_word(word)
        for i, letter in enumerate(word):
            if letter not in keyboard_letter_mistakes.keys():
                continue
            for adjacent_letter in keyboard_letter_mistakes[letter]:
                permutation = list(word)
                permutation[i] = adjacent_letter if adjacent_letter is not None else permutation[i]
                self.permutations.append("".join(permutation))

    def double_constants(self, word):
        double_const_dict = {const: 2*const for const in lowercase_letters}
        reverse_double_const_dict = reverse_dict(double_const_dict)
        self.permutate(word, double_const_dict, reverse_double_const_dict)

    def wrong_constants(self, word):
        single_letter_confusion = {"b": "p", "d": "t", "g": "k", "g": "j", "d": "g", "g": "v", "f": "v", "d": "j", "k": "t", "c": "s"}
        reverse_single_letter_confusion = reverse_dict(single_letter_confusion)
        self.permutate(word, single_letter_confusion, reverse_single_letter_confusion)

        double_letter_confusion = {"bb":"pp", "dd":"tt", "gg":"kk", "ld":"ll", "nd":"nn", "rd":"rr", "ds":"ss", "dt":"tt"}
        reverse_double_letter_confusion = reverse_dict(double_letter_confusion)
        self.permutate(word, double_letter_confusion, reverse_double_letter_confusion)

    def silent_d(self, word):
        silent_d_dict = {"ld": "l", "nd": "n", "rd": "r"}
        reverse_silent_d_dict = reverse_dict(silent_d_dict)
        self.permutate(word, silent_d_dict, reverse_silent_d_dict)

    def silent_h(self, word):
        missing_h_dict = {"hj": "j", "hv": "v"}
        reverse_missing_h_dict = reverse_dict(missing_h_dict)
        self.permutate(word, missing_h_dict, reverse_missing_h_dict)

    def other_silent(self, word):
        silent_letters_dict = {"nt":"n", "st": "s", "et": "e", "lv": "l", "vt": "v"}
        reverse_silent_letters_dict = reverse_dict(silent_letters_dict)
        self.permutate(word, silent_letters_dict, reverse_silent_letters_dict)

        silent_letters = ["g", "t", "v"]

        for i in range(len(word) + 1):
            for letter in silent_letters:
                new_word = word[:i] + letter + word[i:]
                self.permutations.append(new_word)
    
    def wrong_vocal(self, word): 
        wrong_vocal_dict = {"a": ["æ", "e"], "e": ["æ", "i"], "o": "u", "ø": "y", "æ": "i", "å": ["u", "o"]}
        reverse_wrong_vocal_dict = {"e": "a", "i": ["æ", "e"], "u": ["å", "o"], "y": "ø", "o": "å", "æ": ["a", "e"]}
        self.permutate(word, wrong_vocal_dict, reverse_wrong_vocal_dict)

    def get_permutations(self, word):
        self.permutations = []
        #self.keyboard_mistakes(word)
        self.double_constants(word)
        self.wrong_constants(word)
        self.silent_d(word)
        self.silent_h(word)
        self.other_silent(word)
        self.wrong_vocal(word)
        return list(set(self.permutations))