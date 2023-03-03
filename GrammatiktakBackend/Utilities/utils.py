# collection of frequenctly used functions
# use as often as possible to avoid code duplication


# input all words from sentence, index (in words), word
# output list of start and end index in sentence
def find_index(all_words_from_sentence, index_of_word_in_all_words, word):
    start_index = sum([len(word) for word in all_words_from_sentence[:index_of_word_in_all_words]]) + len(all_words_from_sentence[:index_of_word_in_all_words])
    end_index = start_index + len(word)
    return [start_index, end_index]

# input sentence
# output lowercased words with <br> removed
# if split_sentence then always lowercase = Falses
def prepare_sentence(sentence, lowercase=True, split_sentences=False) -> str:
    if split_sentences:
        sentences = sentence.split("<br>")
        return [sent.split() for sent in sentences]
    elif lowercase: 
        return sentence.replace("<br>", " ").lower().split()
    return sentence.replace("<br>", " ").split()

# This can be used to move index based on <br> if needed
# This should be done in the module before returning to the main script
def move_index_based_on_br(errors, sentence):
    pass

# sort errors based on beginning index
def sort_errors(errors):
    return sorted(errors, key=lambda x: x[2][1])

# this function needs to be updated whenever a module is added
# currently runs the following logic:
    # the first instance of a correction is always punctuation
    # the second instance of a correction is always capitalization
def concat_errors(errors):
    elements = {}
    for sublist in errors:
        key = (sublist[2][0], sublist[2][1])
        if key in elements.keys():
            if elements[key][-1] in ".,":
                punctuation = elements[sublist[2]][-1]
                elements[key][1] = sublist[1] + punctuation
                elements[key][3] += " " + sublist[3]
            else:
                elements[key][1] = sublist[1][:-1]
                elements[key][3] += " " + sublist[3]
        else:
            elements[key] = sublist
    concatenated_error = list(elements.values())
    return sort_errors(concatenated_error)