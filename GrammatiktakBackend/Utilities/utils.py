# input all words from sentence, index (in words), word
# output list of start and end index in sentence
def find_index(all_words_from_sentence, index_of_word_in_all_words, word):
    start_index = sum([len(word) for word in all_words_from_sentence[:index_of_word_in_all_words]]) + len(all_words_from_sentence[:index_of_word_in_all_words])
    end_index = start_index + len(word)
    return [start_index, end_index]

# input sentence
# output lowercased words with <br> removed
def prepare_sentence(sentence) -> str:
    return sentence.replace("<br>", " ").lower().split()