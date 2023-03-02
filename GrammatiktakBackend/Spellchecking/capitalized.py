from Utilities.utils import prepare_sentence, find_index

class CapitalizationCorrector:
    def __init__(self) -> None:
        pass

    # creates comma error message
    def create_capitaliztion_error_message(self, word_to_correct, all_words_from_sentence, index_of_word_in_all_words, missing_capitalization) -> list:
        error_description = f"." if missing_capitalization else f"."
        previous_index = find_index(all_words_from_sentence, index_of_word_in_all_words, word_to_correct)
        if missing_capitalization:
            wrong_word, right_word = word_to_correct, word_to_correct[:-1]
        else:
            wrong_word, right_word  = word_to_correct, word_to_correct + ","
        return [wrong_word, right_word, previous_index, error_description]

    # use this function to get errors
    def correct_capitalization(self, sentence):
        words = prepare_sentence(sentence, lowercase=False)
        full_stop = [True if words[i][-1] == "." else False for i in range(len(words))]
        previous_capitalization = [True if words[i][0].isupper() else False for i in range(len(words))]
        error_missing_capitalization = [True if full_stop[i] and not previous_capitalization[i+1] else False for i in range(len(words)-1)]
        