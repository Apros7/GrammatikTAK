
# checking every verb for nutids-r:
# if verb after noun (subject of sentence) then nutids-r
# Possible improvement: check if other endings are correct


from Utilities.utils import prepare_sentence, find_index, move_index_based_on_br

class TenseCorrector():
    def __init__(self) -> None:
        pass

    def create_nutidsr_error_message(self, word_to_correct, all_words_from_sentence, index_of_word_in_all_words, missing_nutidsr) -> list:
        previous_index = find_index(all_words_from_sentence, index_of_word_in_all_words, word_to_correct)
        if missing_nutidsr:
            error_description = f"Der mangler et nutids-r på '{word_to_correct}'."
            wrong_word, right_word = word_to_correct, word_to_correct + "r"
        else:
            wrong_word, right_word  = word_to_correct, word_to_correct[:-1]
            error_description = f"Der skal ikke være nutids-r på '{word_to_correct}'."
        return [wrong_word, right_word, previous_index, error_description]

    def check_if_nutidsr(self, word):
        return True if word[-1] == "r" else False

    def correct_nutidsr(self, sentence, pos):
        words = prepare_sentence(sentence)
        verbs = [True if pos_tag[1] == "VERB" else False for pos_tag in pos]
        should_be_nutids_r = [True if verbs[i] and pos[i-1] == "NOUN" else False for i in range(1, len(verbs))]
        should_be_nutids_r = [False] + should_be_nutids_r
        is_nutids_r = [self.check_if_nutidsr(words[i]) and verbs for i in range(len(words))]
        missing_nutidsr = [True if verbs[i] and not is_nutids_r[i] and should_be_nutids_r[i] else False for i in range(len(verbs))]
        error_message_missing_nutidsr = [self.create_nutidsr_error_message(words[i], words, i, True) for i in range(len(verbs)) if missing_nutidsr[i]]
        wrong_nutidsr = [True if verbs[i] and is_nutids_r[i] and not should_be_nutids_r[i] else False for i in range(len(verbs))]
        error_message_wrong_nutidsr = [self.create_nutidsr_error_message(words[i], words, i, False) for i in range(len(verbs)) if wrong_nutidsr[i]]
        return error_message_missing_nutidsr + error_message_wrong_nutidsr


    def correct_tense(self, sentence, pos):
        return self.correct_nutidsr(sentence, pos)