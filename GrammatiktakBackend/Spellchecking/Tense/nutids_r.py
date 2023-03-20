
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

    def edge_cases(self, words, pos, should_be_nutids_r, verbs_to_check):
        # Check for question: Vil du invitere
        edge_case1_should_be_nutidsr = [False if pos[i-2][0] == "AUX" and (pos[i-1][0] == "NOUN" or pos[i-1][0] == "PRON") else None for i in range(2, len(verbs_to_check))] 
        # Check for "og": Jeg glæder mig til at se og invitere mine gæster
        edge_case2_should_be_nutidsr = [should_be_nutids_r[i-2] if words[i-1] == "og" and verbs_to_check[i] else None for i in range(2, len(verbs_to_check))]
        # Check for "mange": Mange cykler i skole
        edge_case3_should_be_nutidsr = [True if words[i-1] == "mange" and verbs_to_check[i] else None for i in range(1, len(verbs_to_check))]
        # No edge cases for first two words
        edge_case_no_nutidsr = [None, True if edge_case3_should_be_nutidsr[0] is not None else None]
        for i in range(len(edge_case1_should_be_nutidsr)):
            if edge_case1_should_be_nutidsr[i] is not None:
                edge_case_no_nutidsr.append(edge_case1_should_be_nutidsr[i])
            elif edge_case2_should_be_nutidsr[i] is not None:
                edge_case_no_nutidsr.append(edge_case2_should_be_nutidsr[i])
            elif edge_case3_should_be_nutidsr[i] is not None:
                edge_case_no_nutidsr.append(edge_case3_should_be_nutidsr[i])
            else:
                edge_case_no_nutidsr.append(None)
        should_be_nutids_r_with_edge_cases = [edge_case_no_nutidsr[i] if edge_case_no_nutidsr[i] is not None else should_be_nutids_r[i] for i in range(len(edge_case_no_nutidsr))]
        return should_be_nutids_r_with_edge_cases


    def correct_nutids_r(self, sentence, pos):
        words = prepare_sentence(sentence)
        verbs_to_check = [True if pos[i][0] == "VERB" and pos[i][2]["Tense"] == "Pres" else False for i in range(len(pos))]
        should_be_nutids_r = [True if verbs_to_check[0] else False] + [True if verbs_to_check[i] and (pos[i-1][0] == "NOUN" or pos[i-1][0] == "PRON" or pos[i+1][0] == "NOUN" or pos[i+1][0] == "PRON") else False for i in range(1, len(verbs_to_check)-1)]
        should_be_nutids_r += [True if verbs_to_check[-1] and (pos[-2][0] == "NOUN" or pos[-2][0] == "PRON") else False]
        should_be_nutids_r_with_edge_cases = self.edge_cases(words, pos, should_be_nutids_r, verbs_to_check)
        is_nutids_r = [self.check_if_nutidsr(words[i]) if verb_to_check else False for i, verb_to_check in enumerate(verbs_to_check)]
        missing_nutidsr = [True if not is_nutids_r[i] and should_be_nutids_r_with_edge_cases[i] else False for i in range(len(is_nutids_r))]
        error_message_missing_nutidsr = [self.create_nutidsr_error_message(words[i], words, i, True) for i in range(len(is_nutids_r)) if missing_nutidsr[i]]
        wrong_nutidsr = [True if is_nutids_r[i] and not should_be_nutids_r_with_edge_cases[i] else False for i in range(len(is_nutids_r))]
        error_message_wrong_nutidsr = [self.create_nutidsr_error_message(words[i], words, i, False) for i in range(len(is_nutids_r)) if wrong_nutidsr[i]]
        return error_message_missing_nutidsr + error_message_wrong_nutidsr

    def test(self, tagger):
        lines = open("Datasets/nutids_r_test.csv").readlines()
        correct = 0
        total = len(lines)
        for line in lines:
            wrong, right = line.split(",")
            right = right.strip()
            pos = tagger.get_tags(wrong)[0]
            errors = self.correct_nutids_r(wrong, pos)
            for error in errors:
                wrong = wrong.replace(error[0], error[1])
            if wrong == right:
                correct += 1
            else:
                print(errors)
                print(wrong)
                print(right)
                print(len(wrong), len(right))
                print([x[0] for x in pos])
                print("\n")
        print(f"Correct: {correct}/{total}")
        