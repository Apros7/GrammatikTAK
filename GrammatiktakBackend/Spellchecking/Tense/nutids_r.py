
# checking every verb for nutids-r:
# if verb after noun (subject of sentence) then nutids-r
# Possible improvement: check if other endings are correct

from Utilities.utils import prepare_sentence, find_index, move_index_based_on_br

hjælpeverber = ["er", "har", "kan", "vil", "skal", "må"]
uregelmæssige_verber = {"gør": "gøre", "gøre": "gør"}

class NutidsRCorrector():
    def __init__(self):
        pass    

    def create_nutidsr_error_message(self, word_to_correct, all_words_from_sentence, index_of_word_in_all_words, missing_nutidsr) -> list:
        previous_index = find_index(all_words_from_sentence, index_of_word_in_all_words, word_to_correct)
        if missing_nutidsr:
            error_description = f"Der mangler et nutids-r på '{word_to_correct}'."
            wrong_word, right_word = word_to_correct, word_to_correct + "r"
            if wrong_word in uregelmæssige_verber:
                right_word = uregelmæssige_verber[wrong_word]
        else:
            error_description = f"Der skal ikke være nutids-r på '{word_to_correct}'."
            wrong_word, right_word  = word_to_correct, word_to_correct[:-1]
            if wrong_word in uregelmæssige_verber:
                right_word = uregelmæssige_verber[wrong_word]
        return [wrong_word, right_word, previous_index, error_description]
    
    def check_if_nutidsr(self, word):
        return True if word[-1] == "r" else False

    def concat_edge_cases(self, edge_cases):
        edge_case_final = []
        for i in range(len(edge_cases[0])):
            add_none = True
            for edge_case in edge_cases:
                if edge_case[i] is not None:
                    edge_case_final.append(edge_case[i])
                    add_none = False
            if add_none:
                edge_case_final.append(None)
        return edge_case_final

    def edge_cases_should_be_nutids(self, words, pos, should_be_nutids_r, verbs_to_check):
        edge_cases = []
        # Check for question: Vil du invitere
        edge_cases.append(2*[None] + [False if pos[i-2][0] == "AUX" and (pos[i-1][0] == "NOUN" or pos[i-1][0] == "PRON") else None for i in range(2, len(verbs_to_check))] )
        # Check for "og": Jeg glæder mig til at se og invitere mine gæster
        edge_cases.append(2*[None] + [should_be_nutids_r[i-2] if words[i-1] == "og" and verbs_to_check[i] else None for i in range(2, len(verbs_to_check))])
        # Check for "mange": Mange cykler i skole
        edge_cases.append([None] + [True if words[i-1] == "mange" and verbs_to_check[i] else None for i in range(1, len(verbs_to_check))])
        # Check for at: Jeg kan godt lide at spille guitar
        edge_cases.append([None] + [False if words[i-1] == "at" and verbs_to_check[i] else None for i in range(1, len(verbs_to_check))])

        edge_case_should_be_nutidsr = self.concat_edge_cases(edge_cases)
        self.save1 = edge_case_should_be_nutidsr
        self.save2 = should_be_nutids_r
        should_be_nutids_r_with_edge_cases = [edge_case_should_be_nutidsr[i] if edge_case_should_be_nutidsr[i] is not None else should_be_nutids_r[i] for i in range(len(edge_case_should_be_nutidsr))]
        return should_be_nutids_r_with_edge_cases


    def correct_nutids_r(self, sentence, pos):
        words = prepare_sentence(sentence, clean=True)
        print(words)
        print([pos[i][0] for i in range(len(pos))])
        verbs_to_check = [True if pos[i][0] == "VERB" and pos[i][2]["Tense"] == "Pres" and words[i] not in hjælpeverber else False for i in range(len(pos))]
        should_be_nutids_r = [True if verbs_to_check[0] else False] + [True if verbs_to_check[i] and (pos[i-1][0] == "NOUN" or pos[i-1][0] == "PRON" or pos[i+1][0] == "NOUN" or pos[i+1][0] == "PRON") else False for i in range(1, len(verbs_to_check)-1)]
        should_be_nutids_r += [True if verbs_to_check[-1] and (pos[-2][0] == "NOUN" or pos[-2][0] == "PRON") else False]
        should_be_nutids_r_with_edge_cases = self.edge_cases_should_be_nutids(words, pos, should_be_nutids_r, verbs_to_check)
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
                print("edge cases:    ", self.save1)
                print("no edge cases: ", self.save2)
                print(errors)
                print(wrong)
                print(right)
                #print(*pos, sep="\n")
                print("\n")
        print(f"Correct: {correct}/{total}")
        