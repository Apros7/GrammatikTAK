from Utilities.utils import prepare_sentence, find_index

class CapitalizationCorrector:
    def __init__(self) -> None:
        pass

    # creates comma error message
    def create_capitalization_error_message(self, word_to_correct, all_words_from_sentence, index_of_word_in_all_words, missing_capitalization) -> list:
        error_description = f"'{word_to_correct.title()}' skal starte med stort, da det er starten på en ny sætning." if missing_capitalization else f"'{word_to_correct}' skal ikke starte med stort."
        previous_index = find_index(all_words_from_sentence, index_of_word_in_all_words, word_to_correct)
        if missing_capitalization:
            wrong_word, right_word = word_to_correct, word_to_correct.title()
        else:
            wrong_word, right_word  = word_to_correct, word_to_correct.lower()
        return [wrong_word, right_word, previous_index, error_description]

    # corrects all instances of i
    def correct_i(self, sentence) -> str:
        pass

    def find_ner_errors(self, sentence) -> list:
        pass

    def find_basic_errors(self, sentence) -> list:
        words_for_every_sentence = prepare_sentence(sentence, split_sentences=True)
        words = prepare_sentence(sentence, lowercase=False)
        full_stop = [True if word[-1] == "." else False for sent in words_for_every_sentence for word in sent]
        previous_capitalization = [True if word[0].isupper() else False for sent in words_for_every_sentence for word in sent]
        first_word_in_sentence = [True if word == sent[0] else False for sent in words_for_every_sentence for word in sent]
        # if there is a full stop and the word is not capitalized
        error_missing_capitalization = [True if (full_stop[i] or first_word_in_sentence[i+1]) and not previous_capitalization[i+1] else False for i in range(len(words)-1)]
        # Needs to take care of first word: correct if not capitalized
        error_missing_capitalization.insert(0, True if not previous_capitalization[0] else False)
        error_messages_missing_capitalization = [self.create_capitalization_error_message(words[i], words, i, True) for i in range(len(words)) if error_missing_capitalization[i]]
        # if there is not a full stop and the word is capitalized
        error_wrong_capitalization = [True if not full_stop[i] and previous_capitalization[i+1] and not first_word_in_sentence[i+1] else False for i in range(len(words)-1)]
        # needs to take care of first word. Never correct in this case
        error_wrong_capitalization.insert(0, False)
        error_messages_wrong_capitalization = [self.create_capitalization_error_message(words[i], words, i, False) for i in range(len(words)) if error_wrong_capitalization[i]]
        return error_messages_missing_capitalization + error_messages_wrong_capitalization

    # use this function to get errors
    def correct_capitalization(self, sentence):
        errors = self.find_basic_errors(sentence)
        return errors

        