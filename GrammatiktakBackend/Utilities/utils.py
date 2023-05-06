# collection of frequenctly used functions
# use as often as possible to avoid code duplication

import re
import string
from Utilities.error_handling import Error, ErrorList

# input json_data
# returns (is_empty_or_feedback, feedback, input, potential output)
# used in main to filter incoming traffic
def check_empty_input_or_feedback(json_data):

    input_string = json_data["sentence"]
    feedback = json_data["feedback"]

    # check for feedback
    if feedback != None:
        return True, feedback, input_string, "Saved"

    # check if empty request
    if input_string.strip() == "":
        return True, feedback, input_string, []
    else:
        return False, feedback, input_string, None

# input all words from sentence, index (in words), word
# output list of start and end index in sentence
def find_index(all_words_from_sentence, index_of_word_in_all_words, word):
    start_index = sum([len(word) for word in all_words_from_sentence[:index_of_word_in_all_words]]) + len(all_words_from_sentence[:index_of_word_in_all_words])
    end_index = start_index + len(word)
    return [start_index, end_index]

# input sentence
# output lowercased words with <br> removed
# if split_sentence then always lowercase = Falses
def prepare_sentence(sentence, lowercase=True, split_sentences=False, clean=False) -> str:
    if clean:
        sentence = clean_sentence(sentence)
    if split_sentences:
        sentences = sentence.split("<br>")
        return [sent.split() for sent in sentences]
    elif lowercase: 
        return sentence.replace("<br>", " ").lower().split()
    return sentence.replace("<br>", " ").split()

def clean_sentence(sentence):
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
    for error in errors:
        (start, end) = error[2][0], error[2][1]
        # Adjust for <br> tags before the start index
        for br_index in br_indexes:
            if br_index < start:
                start += 3
                end += 3
        # Adjust for <br> tags between the start and end indexes
            elif br_index > start and br_index < end:
                end += 3
        error[2][0], error[2][1] = start, end
    return ErrorList([Error().from_list(error) for error in errors])

# sort errors based on beginning index
def sort_errors(errors):
    return sorted(errors, key=lambda x: x[2][1])

# this function needs to be updated whenever a module is added
# currently runs the following logic:
    # the first instance of a correction is always punctuation
    # the second instance of a correction is always capitalization
    # the third instance of a correction is always tense
def concat_errors(errors):
    elements = {}
    for sublist in errors:
        key = (sublist[2][0], sublist[2][1])
        if key in elements.keys():
            if elements[key][1][0].isupper():
                elements[key][1] = elements[key][1].replace(sublist[0].capitalize(), sublist[1].capitalize())
                elements[key][3] += " " + sublist[3]
            elif elements[key][0][0].isupper():
                elements[key][1] = elements[key][1].replace(sublist[0], sublist[1])
                elements[key][3] += " " + sublist[3]
            elif elements[key][1][-1] in ".,":
                punctuation = elements[key][1][-1]
                elements[key][1] = sublist[1] + punctuation
                elements[key][3] += " " + sublist[3]
            elif elements[key][0][-1] in ".,":
                elements[key][1] = sublist[1][:-1]
                elements[key][3] += " " + sublist[3]
        else:
            elements[key] = sublist
    concatenated_error = list(elements.values())
    return concatenated_error


# This function is used to check if the index from a module is correct
def check_if_index_is_correct(errors, sentence):
    should_be = [errors[i][0] for i in range(len(errors))]
    actual = [sentence[errors[i][2][0]:errors[i][2][1]] for i in range(len(errors))]
    for i in range(len(should_be)):
        print("Should be: ", should_be[i], ". Actual: ", actual[i], ". Equal?: ", should_be[i] == actual[i])
    
    print("BE AWARE:")
    print("If you use this function directly in your script it might return False even though your function works perfectly!")
    print("Instead, launch the GrammatikTAK website locally, hook it up to your backend, and try it out.")
    print("This is due to some features in the front that changes the html code to fit.")

# This function is used to test a new module:

        