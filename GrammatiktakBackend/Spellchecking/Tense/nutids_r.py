
# checking every verb for nutids-r:
# if verb after noun (subject of sentence) then nutids-r
# Possible improvement: check if other endings are correct

from Utilities.utils import prepare_sentence, find_index, move_index_based_on_br

class NutidsRCorrector():
    def __init__(self):
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

    def correct_nutids_r(self, sentence, pos):
        words = prepare_sentence(sentence)
        verbs_to_check = [True if pos[i][0] == "VERB" and pos[i][2]["Tense"] == "Pres" else False for i in range(len(pos))]
        should_be_nutids_r = [False] + [True if verbs_to_check[i] and (pos[i-1][0] == "NOUN" or pos[i-1][0] == "PRON")else False for i in range(1, len(verbs_to_check))]
        is_nutids_r = [self.check_if_nutidsr(words[i]) if verb_to_check else False for i, verb_to_check in enumerate(verbs_to_check)]
        missing_nutidsr = [True if not is_nutids_r[i] and should_be_nutids_r[i] else False for i in range(len(is_nutids_r))]
        error_message_missing_nutidsr = [self.create_nutidsr_error_message(words[i], words, i, True) for i in range(len(is_nutids_r)) if missing_nutidsr[i]]
        wrong_nutidsr = [True if is_nutids_r[i] and not should_be_nutids_r[i] else False for i in range(len(is_nutids_r))]
        error_message_wrong_nutidsr = [self.create_nutidsr_error_message(words[i], words, i, False) for i in range(len(is_nutids_r)) if wrong_nutidsr[i]]
        return error_message_missing_nutidsr + error_message_wrong_nutidsr