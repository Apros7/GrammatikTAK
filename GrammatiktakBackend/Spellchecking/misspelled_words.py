
# this is build of the following report (p. 26-) (dog hovedsageligt fra p. 38-): 
# https://dsn.dk/wp-content/uploads/2021/01/Saadan.staver.vi_.pdf
# decided to hard code basic spellchecker as levenshtein distance did not work well
# context based path should be applied later on

from Utilities.utils import prepare_sentence, find_index, move_index_based_on_br
#from polyleven import levenshtein # add polyleven to requirements

# no correction when symbols in word
NO_CORRECTION = "'-_.,;:!?()[]{}"
# symbols that are 
STRIPPED_SYMBOLS = ".,'"

# loads dictionary, returns set object
def load_dictionary():
    with open("Datasets/ordlisteFuldform2021OneRow.csv", "r") as f:
        dictionary = set(f.read().splitlines())
    return dictionary

def check_letter_in_word(letter, word, consecutive_frequency):
    return letter*consecutive_frequency in word

class MisspelledWordsCorrector():
    def __init__(self):
        self.dictionary = load_dictionary()

    def test_replace_letter(self, word, letter1, letter2, letter_len=1):
        if letter_len != 1 and letter_len != 2:
            raise Exception("Not implemented for letter len > 2")
        if letter_len == 1:
            for i in range(len(word)):
                if word[i] == letter1:
                    potential_word = word[:i] + letter2 + word[i+1:]
                    if potential_word in self.dictionary:
                        return potential_word
        if letter_len == 2:
            for i in range(len(word)-1):
                if word[i:i+1] == letter1:
                    potential_word = word[:i] + letter2 + word[i+2:]
                    if potential_word in self.dictionary:
                        return potential_word

    # test if letter added to word in every position gives good prediction:
    def test_letter_addition(self, word, letter, front_words=None, end_words=None):
        print(f"Testing letter addition to word: {word}")
        print(f"Front words: {front_words}")
        print(f"End words: {end_words}")
        for i in range(len(word)):
            if front_words is not None:
                if word[i] not in front_words:
                    continue
            potential_word = word[:i+1] + letter + word[i+1:] 
            if potential_word in self.dictionary:
                return potential_word

        for i in range(len(word)):
            if end_words is not None:
                if word[i] not in end_words:
                    continue
            potential_word = word[:i] + letter + word[i:] 
            if potential_word in self.dictionary:
                return potential_word

    # test if a silent word added or delete give a reasonable prediction
    def test_silent_letter(self, word, letter, front_words=None, end_words=None):
        if check_letter_in_word(letter, word, 1):
            potential_word = word.replace(letter, "")
            print(potential_word)
            if potential_word in self.dictionary:
                return potential_word
        return self.test_letter_addition(word, letter, front_words, end_words)
    
    def create_misspelling_error(self, word_before_correction, word_after_correction, all_words_from_sentence, index_of_word_in_all_words):
        previous_index = find_index(all_words_from_sentence, index_of_word_in_all_words, word_before_correction)
        error_description = f"'{word_before_correction}' ser ikke ud til at være korrekt. Passer '{word_after_correction}' bedre ind?."
        return [word_before_correction, word_after_correction, previous_index, error_description]

    # functions to correct misspelled words from simple to complex
    def mistake_is_j_or_v(self, word):
        if check_letter_in_word("j", word, 2):
            if word.replace("jj", "j") in self.dictionary():
                return word.replace("jj", "j")
        elif check_letter_in_word("v", word, 2):
            if word.replace("vv", "v") in self.dictionary():
                return word.replace("vv", "v")

    def silent_d(self, word):
        FRONT_WORDS = "lnr"
        END_WORDS = "st"
        return self.test_silent_letter(word, "d", FRONT_WORDS, END_WORDS)

    def other_silent_words(self, word):
        END_H_WORDS = "jv"
        SILENT_WORDS = "gtv"
        potential_word = self.test_silent_letter(word, "h", None, END_H_WORDS)
        if potential_word is not None: return potential_word
        for letter in SILENT_WORDS:
            if check_letter_in_word(letter, word, 1):
                potential_word = word.replace(letter, "")
                if potential_word in self.dictionary:
                    return potential_word
        
        for letter in SILENT_WORDS:
            potential_word = self.test_silent_letter(word, letter, None, None)
            if potential_word is not None: return potential_word
            
    def double_consonant(self, word):
        LETTERS = "drs"
        for letter in LETTERS:
            if check_letter_in_word(letter, word, 2):
                if word.replace(letter+letter, letter) in self.dictionary:
                    return word.replace(letter+letter, letter)
            potential_word = self.test_letter_addition(word, letter, letter, None) 
            if potential_word is not None: return potential_word
    
    def consonant_confusing(self, word):
        # single letter
        single_letter_confusion = {"b": "p", "d": "t", "g": "k", "g": "j", "d": "g", "g": "v", "f": "v", "d": "j", "k": "t", "c": "s"}
        for letter in single_letter_confusion.keys():
            if check_letter_in_word(letter, word, 1):
                potential_word = self.test_replace_letter(word, letter, single_letter_confusion[letter], 1)
                if potential_word is not None:
                    return potential_word

        # double letter
        double_letter_confusion = {"bb":"pp", "dd":"tt", "gg":"kk", "ld":"ll", "nd":"nn", "rd":"rr", "ds":"ss", "dt":"tt"}
        for letter in double_letter_confusion.keys():
            if check_letter_in_word(letter, word, 1):
                potential_word = self.test_replace_letter(word, letter, double_letter_confusion[letter], 2)
                if potential_word is not None:
                    return potential_word

    # orders mistakes from simple to complex
    def predict_correct_word(self, word) -> str:
        ordered_prediction_functions = [self.mistake_is_j_or_v, self.silent_d, self.other_silent_words, self.double_consonant, self.consonant_confusing]
        for function in ordered_prediction_functions:
            corrected_word = function(word)
            if corrected_word is None:
                continue
            if corrected_word in self.dictionary:
                print(word, function)
                return corrected_word
    
    # finds all misspelled words in sentence and corrects them
    def correct_misspelled_words(self, sentence):
        words = [word[:-1] if word[-1] in STRIPPED_SYMBOLS else word for word in prepare_sentence(sentence)]
        misspelled_words = [word not in self.dictionary for word in words]
        corrected_words = [(words[i], self.predict_correct_word(words[i]), i) for i in range(len(words)) if misspelled_words[i]]
        error_messages_corrected_words = [self.create_misspelling_error(corrected_word[0], corrected_word[1], words, corrected_word[2]) for corrected_word in corrected_words if corrected_word[1] is not None]
        return error_messages_corrected_words
    
    # function to see abilities:
    def test_spellchecker(self):
        sentence = "fal krit skedt fjord julpet egenlig selvskab redede litter cykkel smøret profesor skuppede længte skyldede pusse soldt sovn "
        correct_sentence = "fald kridt sket fjor hjulpet egentlig selskab reddede liter cykel smørret professor skubbede længde skyllede pudse solgt sogn"
        corrected_words = [error[1] for error in self.correct_misspelled_words(sentence)]
        print(f"Sentence: {sentence}")
        print(f"Predictions: {corrected_words}")
        print(f"Correct sentence: {correct_sentence}")

    
