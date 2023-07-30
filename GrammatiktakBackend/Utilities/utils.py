# collection of frequenctly used functions
# use as often as possible to avoid code duplication

import re
import string
from Utilities.error_handling import Error, ErrorList


def get_pos_without_information(pos): return [x[0] for x in pos]        

# input json_data
# returns (is_empty_or_feedback, feedback, input, potential output)
# used in main to filter incoming traffic
def check_empty_input_or_feedback(json_data):

    input_string = json_data["sentence"]
    feedback = json_data["feedback"]

    if feedback != None:
        return True, feedback, input_string, "Saved"

    # check if empty request
    if input_string.strip() == "":
        return True, feedback, input_string, []
    else:
        return False, feedback, input_string, None

# input all words from sentence, index (in words), word
# output list of start and end index in sentence
# This needs more work if any other modules that change the indexes of the original sentence

class IndexFinder():
    """
    Whenever you manipulate the sentence, you should tell indexfinder which index you change, and what you changed it to
    You can then use find_index to find the index giving it the index of the manipulated sentence.
    Freeze index finder before each module
    """

    def __init__(self, original_sentence) -> None: 
        self.original_sentence = original_sentence; self.original_words = original_sentence.split(" ")
        self.indexes_changed_from_input_words = []; self.changed_to = [(self.original_words[i], False) for i in range(len(self.original_words))]
        self.freeze()

    def add_index(self, index, changed_to, add=False):
        if add: self.changed_to.insert(self.true_index(index), (changed_to, True))
        else: self.changed_to[self.true_index(index)] = (changed_to, False)

    def true_index(self, index): 
        for i, word in enumerate(self.frozen_lst):
            if word[0] == "" and i <= index: index += 1
            if word[1] and i <= index: index -= 1
        return index

    def freeze(self): self.frozen_lst = self.changed_to.copy()
    def __call__(self): return self.frozen_lst

    def find_index(self, index_of_word_in_all_words, word):
        true_index = self.true_index(index_of_word_in_all_words)
        start_index = sum([len(word) for word in self.original_words[:true_index]]) + len(self.original_words[:true_index])
        number_of_words_to_consider = len(word.split())
        true_word_length = -1
        non_added_lst = [el for el in self.frozen_lst if not el[1]]
        while number_of_words_to_consider > 0 and true_index < len(non_added_lst):
            true_word_length += len(non_added_lst[true_index][0]) + 1
            if non_added_lst[true_index][0] != "":
                number_of_words_to_consider -= 1
            true_index += 1
        word_has_punctuation = word[-1] in string.punctuation
        sentence_ends_with_punctuation = False if len(non_added_lst[true_index-1][0]) == 0 else non_added_lst[true_index-1][0][-1] in string.punctuation
        if not word_has_punctuation and sentence_ends_with_punctuation: true_word_length -= 1
        end_index = start_index + true_word_length
        return [start_index, end_index]

# input sentence
# output lowercased words with <br> removed
# if split_sentence then always lowercase = Falses
def prepare_sentence(sentence, lowercase=False, split_sentences=False, clean=False) -> str:
    """
    Will always replace <br> with " " unless split_sentences = True, which will then give list of lists of words
    Clean: replace <br> with " " and remove all punctuation.
    Lowercase: lowercase
    Returns list of words
    """
    if clean:
        sentence = clean_sentence(sentence)
    if split_sentences:
        sentences = sentence.split("<br>")
        return [sent.split() for sent in sentences]
    elif lowercase: 
        return sentence.replace("<br>", " ").lower().split()
    return sentence.replace("<br>", " ").split()

def clean_sentence(sentence):
    sentence = sentence.replace("<br>", " ")
    words = sentence.split()
    cleaned_words = []
    for word in words:
        if all(char in string.punctuation for char in word):
            cleaned_words.append(word)
        else:
            cleaned_word = word.translate(str.maketrans("", "", string.punctuation))
            cleaned_words.append(cleaned_word)
    sentence = " ".join(cleaned_words)
    return sentence

# This can be used to move index based on <br> if needed
# This should be done in the module before returning to the main script
def move_index_based_on_br(errors, sentence):
    br_indexes = [match.start() for match in re.finditer('<br>', sentence)]
    errors = errors.to_list(include_type=True)
    br_space = count_spaces_before_after_br(br_indexes, sentence)
    for error in errors:
        (start, end) = error[2][0], error[2][1]
        for br_index in br_indexes:
            if br_index < start:
                start += 3 + br_space[br_index]
                end += 3 + br_space[br_index]
            elif br_index > start and br_index < end:
                end += 3 + br_space[br_index]
        error[2][0], error[2][1] = start, end
    return ErrorList([Error().from_list(error) for error in errors])

def count_spaces_before_after_br(br_indexes, sentence):
    spaces_dict = {}
    for br_index in br_indexes:
        spaces_before = len(sentence[:br_index]) - len(sentence[:br_index].rstrip())
        spaces_after = len(sentence[br_index + 4:]) - len(sentence[br_index + 4:].lstrip())
        spaces_dict[br_index] = spaces_before + spaces_after
    return spaces_dict

# This function is used to check if the index from a module is correct
def check_if_index_is_correct(errors, sentence, info=True):
    should_be = [errors[i][0] for i in range(len(errors))]
    actual = [sentence[errors[i][2][0]:errors[i][2][1]] for i in range(len(errors))]
    # actual = []
    # for i in range(len(errors)):
    #     words = sentence[errors[i][2][0]:errors[i][2][1]]
    #     if not all(x == "" for x in words.split()): words = " ".join(words.split())
    #     actual.append(words)
    states = []
    for i in range(len(should_be)):
        states.append(should_be[i].lower() == actual[i].lower())
        if info: print("Error says: ", should_be[i].lower(), ". Actual in sentence: ", actual[i].lower(), ". Equal?: ", states[-1], ". Lengths: ", len(should_be[i]), " ", len(actual[i]))
    if info:
        print(" ------------------------------------\n | FINAL STATE IF ALL ADS UP: ", all(states), "|\n ------------------------------------")
        print("BE AWARE:")
        print("Make sure to test with <br> on the frontend side of things!")
    return all(states)

def print_list_of_ErrorList(*args):
    print("ERRORS: ")
    for lst in args:
        for ErrorLst in lst:
            print(ErrorLst.to_list())
    print("END OF ERRORS")