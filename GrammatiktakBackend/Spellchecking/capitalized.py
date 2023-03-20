from Utilities.utils import prepare_sentence, find_index, move_index_based_on_br
import numpy as np

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
    
    # creates I/i error message
    def create_i_error_message(self, word_to_correct, all_words_from_sentence, index_of_word_in_all_words, missing_capitalization) -> list:
        error_description = f"'{word_to_correct.title()}' skal starte med stort, da det står i stedet for nogen." if missing_capitalization else f"'{word_to_correct}' skal ikke starte med stort."
        previous_index = find_index(all_words_from_sentence, index_of_word_in_all_words, word_to_correct)
        if missing_capitalization:
            wrong_word, right_word = word_to_correct, word_to_correct.title()
        else:
            wrong_word, right_word  = word_to_correct, word_to_correct.lower()
        return [wrong_word, right_word, previous_index, error_description]

    # create NER error
    def create_ner_error_message(self, word_to_correct, indexes) -> list:
        error_description = f"'{word_to_correct.title()}' skal starte med stort, da det er et egenavn."
        wrong_word, right_word = word_to_correct, word_to_correct.title()
        return [wrong_word, right_word, indexes, error_description]

    # corrects all instances of i
    def correct_i(self, sentence, pos_tags) -> str:
        words_for_every_sentence = prepare_sentence(sentence, split_sentences=True)
        words = prepare_sentence(sentence, lowercase=False)
        is_capitalized_i = [True if word == "I" else False for sent in words_for_every_sentence for word in sent]
        is_uncapitalized_i = [True if word == "i" else False for sent in words_for_every_sentence for word in sent]
        should_be_capitalized_verb = [True if pos_tags[i+1][0] == "VERB" else False for i in range(len(words)-1)] + [False]
        should_be_capitalized_punctuation = [True] + [True if words[i-1][-1] == "." else False for i in range(1, len(words))]
        should_be_capitalized = [True if should_be_capitalized_verb[i] or should_be_capitalized_punctuation[i] else False for i in range(len(words))]
        # get errors that are not capitalized
        error_messages_missing_capitalization = [self.create_i_error_message(words[i], words, i, True) for i in range(len(words)) if is_uncapitalized_i[i] and should_be_capitalized[i]]
        # get errors that are capitalized
        error_messages_wrong_capitalization = [self.create_i_error_message(words[i], words, i, False) for i in range(len(words)) if is_capitalized_i[i] and not should_be_capitalized[i]]
        return error_messages_missing_capitalization + error_messages_wrong_capitalization

    def check_ner_interval(self, interval_to_check, ner_intervals):
        ner_intervals = np.array(ner_intervals)
        if np.size(ner_intervals) == 0:
            return False
        mask = (ner_intervals[:, 0] <= interval_to_check[0]) & (ner_intervals[:, 1] >= interval_to_check[1])
        return np.any(mask)

    # finds capitalization errors with NER not being capitalized
    def find_ner_errors(self, sentence, ner_tags) -> list:
        words = prepare_sentence(sentence, lowercase=False)
        previous_capitalization = [True if word[0].isupper() else False for word in words]
        ner_indexes = [tag[1] for tag in ner_tags]
        ner_words = [(True, (find_index(words, i, words[i]))) if self.check_ner_interval(find_index(words, i, words[i]), ner_indexes) else (False, []) for i in range(len(words))]
        error_messages_missing_capitalization = [self.create_ner_error_message(words[i], ner_words[i][1]) for i in range(len(words)) if ner_words[i][0] and not previous_capitalization[i]]
        return error_messages_missing_capitalization

    # finds capitalization errors after full stop
    # does not fix ner og i errors
    def find_basic_errors(self, sentence, ner_tags) -> list:
        words_for_every_sentence = prepare_sentence(sentence, split_sentences=True)
        words = prepare_sentence(sentence, lowercase=False)
        full_stop = [True if word[-1] == "." else False for sent in words_for_every_sentence for word in sent]
        previous_capitalization = [True if word[0].isupper() else False for sent in words_for_every_sentence for word in sent]
        first_word_in_sentence = [True if word == sent[0] else False for sent in words_for_every_sentence for word in sent]
        is_i = [True if word.lower() == "i" else False for sent in words_for_every_sentence for word in sent]
        ner_indexes = [tag[1] for tag in ner_tags]
        # i and NER should be skipped
        skip_word = [True if self.check_ner_interval(find_index(words, i, words[i]), ner_indexes) or is_i[i] else False for i in range(len(words))]
        # if there is a full stop and the word is not capitalized
        error_missing_capitalization = [True if (full_stop[i] or first_word_in_sentence[i+1]) and not previous_capitalization[i+1] and not skip_word[i+1] else False for i in range(len(words)-1)]
        # Needs to take care of first word: correct if not capitalized
        error_missing_capitalization.insert(0, True if not previous_capitalization[0] else False)
        error_messages_missing_capitalization = [self.create_capitalization_error_message(words[i], words, i, True) for i in range(len(words)) if error_missing_capitalization[i]]
        # if there is not a full stop and the word is capitalized
        error_wrong_capitalization = [True if not full_stop[i] and previous_capitalization[i+1] and not first_word_in_sentence[i+1] and not skip_word[i+1] else False for i in range(len(words)-1)]
        # needs to take care of first word. Never correct in this case
        error_wrong_capitalization.insert(0, False)
        error_messages_wrong_capitalization = [self.create_capitalization_error_message(words[i], words, i, False) for i in range(len(words)) if error_wrong_capitalization[i]]
        return error_messages_missing_capitalization + error_messages_wrong_capitalization

    # use this function to get errors
    def correct_capitalization(self, sentence, pos_tags, ner_tags) -> list:
        basic_errors = self.find_basic_errors(sentence, ner_tags)
        i_errors = self.correct_i(sentence, pos_tags)
        ner_errors = self.find_ner_errors(sentence, ner_tags)
        return move_index_based_on_br(basic_errors + i_errors + ner_errors, sentence)

        