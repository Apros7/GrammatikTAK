
# from Utilities.utils import prepare_sentence
# from Utilities.error_handling import Error

# NEEDS MASSIVE REFACTORING

from Utilities.utils import prepare_sentence, move_index_based_on_br, find_index
import pickle
from tqdm import tqdm

class AdverbialFinder():
    def __init__(self) -> None:
        pass

    def find_adverbial_led(self, pos_full_lst, sentence, return_pos=False):
        word_classes = [pos_full_lst[i][0] for i in range(len(pos_full_lst))]
        words = prepare_sentence(sentence, lowercase=False, clean=True)
        patterns = [
            ["ADV"], 
            ["ADV", "NOUN"],
            #["ADV", "PRON"],
            #["ADV", "ADJ", "NOUN"],
            #["ADV", "ADJ", "PRON"],
            ["ADV", "CCONJ", "ADV"],
            ["ADV", "DET", "NOUN"],
            #["ADP"],
            ["ADP", "NOUN"],
            #["ADP", "PRON"],
            ["ADP", "VERB"],
            ["ADP", "ADJ", "NOUN"],
            ["ADP", "ADJ", "PRON"], 
        ]

        adverbialled = []
        new_pos = word_classes[:]
        for i in range(len(word_classes)):
            for pattern in patterns:
                if word_classes[i:i+len(pattern)] == pattern:
                    adverbialled.append(" ".join([words[j] for j in range(i, i+len(pattern))]))
                    for j in range(i, i+len(pattern)):
                        new_pos[j] = "ADL"
        
        if return_pos:
            return adverbialled, new_pos
        return adverbialled

class SubjectFinder():
    def __init__(self) -> None:
        pass

    def find_subject(self, word_classes):
        new_pos = word_classes[:]
        for i in range(len(word_classes)):
            if word_classes[i] == "NOUN":
                new_pos[i] = "SBJ"
                if i >= len(word_classes)-1:
                    continue
                if word_classes[i+1] == "CCONJ":
                    new_pos[i+1] = "SBJ"
        return new_pos

class NutidsRCorrector():
    def __init__(self):
        self.can_verb_be_checked = pickle.load(open("Datasets/nutids_r_stem.pickle", "rb"))
        self.get_tense_from_verb = pickle.load(open("Datasets/nutids_r_bøjninger.pickle", "rb"))
        self.buffer = None
        self.adverbialFinder = AdverbialFinder()
        self.subjectFinder = SubjectFinder()
            
    def verbs_should_be_nutids_r(self, words, verbs_to_check):
        should_be_nutids_r1 = [None] + [True if verbs_to_check[i] and self.check_verb_cases(i, (0, "NOUN/PRON")) else None for i in range(1, len(verbs_to_check))]
        should_be_nutids_r2 = [True if verbs_to_check[i] and (self.pos[i+1][0] == "NOUN" or self.pos[i+1][0] == "PRON") else None for i in range(0, len(verbs_to_check)-1)] + [None]
        should_be_nutids_r = [True if should_be_nutids_r1[i] or should_be_nutids_r2[i] else None for i in range(len(should_be_nutids_r1))]
        return should_be_nutids_r

    def verbs_should_not_be_nutids_r(self, words, verbs_to_check):
        should_not_be_nutids_r = [None] + [None for i in range(1, len(verbs_to_check))]
        return should_not_be_nutids_r

    def ignore_adv(self, pos_full_lst):
        _, word_classes = self.adverbialFinder.find_adverbial_led(pos_full_lst, self.current_sentence, return_pos=True)
        return [word_class for word_class in word_classes if word_class != "ADL"]

    def ignore_sbj(self, pos_full_lst):
        word_classes = self.subjectFinder.find_subject(pos_full_lst)
        modified = []
        for i, word_class in enumerate(word_classes):
            if word_class == "SBJ":
                # Check if the previous word is also "hello"
                if i == 0 or word_classes[i-1] != "SBJ":
                    modified.append("NOUN")
            else:
                modified.append(word_class)
        return modified

    def concat_edge_cases(self, words, edge_cases):
        if len(words) < 2:
            return [None]*len(words)
        edge_case_final = []
        for i in range(len(edge_cases[0])):
            add_none = True
            for edge_case in edge_cases:
                if edge_case[i] is not None and add_none:
                    edge_case_final.append(edge_case[i])
                    add_none = False
                    break
                elif edge_case[i] is not None:
                    print(f"CONFLICT: {[edge_case[i] for edge_case in edge_cases]}")
            if add_none:
                edge_case_final.append(None)
        return edge_case_final

    def overruling_edge_cases(self, words, verbs_to_check, should_be_nutids_r):

        ## Priority top to bottom:
        # If already said False or True then other True or False does not matter. First one matters.
        edge_cases = []
        # Check for question: Vil du invitere
        edge_cases.append([False if self.check_verb_cases(i, (0, "NOUN/PRON"), (-1, "AUX/VERB")) else None for i in range(0, len(verbs_to_check))])
        edge_cases.append([None, None] + [False if self.pos[i-2][0] == "AUX" and (self.pos[i-1][0] == "NOUN" or self.pos[i-1][0] == "PRON") else None for i in range(2, len(verbs_to_check))])
        # Check for "og": Jeg glæder mig til at se og invitere mine gæster
        edge_cases.append(2*[None] + [should_be_nutids_r[i-2] if words[i-1] == "og" and verbs_to_check[i] else None for i in range(2, len(verbs_to_check))])
        # Check for "mange" og "som": Mange cykler i skole, Jeg har en mor, som elsker bacon.
        edge_cases.append([None] + [True if (words[i-1] == "mange" or words[i-1] == "som") and verbs_to_check[i] else None for i in range(1, len(verbs_to_check))])
        # Check for "at" in front
        edge_cases.append([None] + [False if words[i-1] == "at" and verbs_to_check[i] else None for i in range(1, len(verbs_to_check))])
        # Check for "Det vil, håber jeg, blive behandlet"
        edge_cases.append([True if verbs_to_check and self.check_verb_cases(i, (0, "VERB"), (-1, "NOUN/PRON"), (-2, "VERB/AUX")) else None for i in range(0, len(verbs_to_check))])
        # Check for "Jeg vil spise"
        edge_cases.append([None] + [False if verbs_to_check[i] and self.check_verb_cases(i, (0, "AUX")) else None for i in range(1, len(verbs_to_check))])
        # Check for "at komme og forelægge"
        edge_cases.append([None] + [False if verbs_to_check[i] and self.check_verb_cases(i, (0, "CCONJ"), (-1, "VERB/AUX"), (-2, "AUX/SCONJ")) else None for i in range(1, len(verbs_to_check))])
        # Check for "skal forhandles af Parlamentet på torsdag og indeholder"
        edge_cases.append([None] + [True if verbs_to_check[i] and self.check_verb_cases(i, (0, "CCONJ"), (-1, "VERB/AUX")) else None for i in range(1, len(verbs_to_check))])
        # Check for "Derfor beder jeg dem gennemgå"
        edge_cases.append([None] + [False if verbs_to_check[i] and self.check_verb_cases(i, (0, "NOUN/PRON"), (-1, "NOUN/PRON"), (-2, "VERB")) else None for i in range(1, len(verbs_to_check))])
        # Check for skal Peter forhandle
        #edge_cases.append([False if self.check_verb_cases(i, (0, "NOUN"), (-1, "VERB")) else None for i in range(0, len(verbs_to_check))])
        

        _, new_pos = self.adverbialFinder.find_adverbial_led(self.pos, self.current_sentence, return_pos=True)
        new_pos = self.subjectFinder.find_subject(new_pos)
        self.buffer = list(zip(words, new_pos))
        self.edge_cases = edge_cases, self.concat_edge_cases(words, edge_cases), self.ignore_sbj(self.ignore_adv(self.pos))
        return self.concat_edge_cases(words, edge_cases)

    def check_verb_cases(self, original_index, *cases):
        pos_with_adv_ignored = self.ignore_adv(self.pos[:original_index])
        pos_with_sbj_ignored = self.ignore_sbj(pos_with_adv_ignored)
        for case in cases:
            index = len(pos_with_sbj_ignored) - 1 + case[0]
            if index < 0 or index >= len(pos_with_sbj_ignored):
                return False
            possibilities = case[1].split("/")
            if pos_with_sbj_ignored[index] not in possibilities:
                return False
        return True

    def should_be_nutids_r(self, words, verbs_to_check):
        should_be_nutids_r_final = self.verbs_should_be_nutids_r(words, verbs_to_check)
        overruling_cases = self.overruling_edge_cases(words, verbs_to_check, should_be_nutids_r_final)
        for i, overruling_case in enumerate(overruling_cases):
            if overruling_case is not None:
                should_be_nutids_r_final[i] = overruling_case
        return should_be_nutids_r_final

    def verbs_to_check(self, words, pos):
        verbs = []
        for i in range(len(pos)):
            if pos[i][0] != "VERB":
                verbs.append(False)
            elif "Tense" not in pos[i][2].keys():
                verbs.append(False)
            elif pos[i][2]["Tense"] != "Pres":
                verbs.append(False)
            else:
                verbs.append(True)
        for i, bool in enumerate(verbs):
            if not bool:
                continue
            word = words[i].strip(",.!?():;")
            try: stemmed_verb = self.can_verb_be_checked[word]
            except: verbs[i] = False; continue
        return verbs

    def make_nutids_r_error_message(self, word_to_correct, all_words_from_sentence, index_of_word_in_all_words, correct_word, to_nutids_r):
        previous_index = find_index(all_words_from_sentence, index_of_word_in_all_words, word_to_correct)
        nutids_r_comment = " med nutids-r"
        if to_nutids_r:
            # None kan erstattes med "med nutids-r", hvis forskellen er et nutids-r
            description = f"{word_to_correct} skal stå i ___ form{nutids_r_comment}, så der står {correct_word}"
        else: 
            description = f"{word_to_correct} skal stå i ___ form{nutids_r_comment}, så der står {correct_word}"
        return [word_to_correct, correct_word, previous_index, description]

    def make_error_messages(self, words, should_be_nutids_r, is_nutids_r, verbs_to_check):
        errors = []
        for i in range(len(words)):
            if len(words[i].strip(",.!?():;")) == 0:
                continue
            verb_to_check = verbs_to_check[i]
            if not verb_to_check:
                continue 
            current_word = words[i].strip(",.!?():;")
            should_be = should_be_nutids_r[i]
            is_nutid = is_nutids_r[i]
            if should_be == is_nutid or is_nutid is None:
                continue
            stemmed_word = self.can_verb_be_checked[current_word]
            if should_be is True:
                to_nutids_r = True
                correct_word = self.get_tense_from_verb[stemmed_word][1]
            else:
                correct_word = self.get_tense_from_verb[stemmed_word][0]
                to_nutids_r = False
            correct_word = words[i].replace(current_word, correct_word)
            error = self.make_nutids_r_error_message(words[i], words, i, correct_word, to_nutids_r)
            errors.append(error)
        return errors

    def is_verbs_nutids_r(self, words, verbs_to_check):
        is_nutids_r = []
        for word, should_check in zip(words, verbs_to_check):
            word = word.strip(",.!?():;")
            if not should_check:
                is_nutids_r.append(None)
                continue
            infinitiv_form, nutids_r_form = self.get_tense_from_verb[self.can_verb_be_checked[word]]
            if word == infinitiv_form:
                is_nutids_r.append(False)
            elif word == nutids_r_form:
                is_nutids_r.append(True)
            else:
                print("ERROR: word is not infinitiv or nutids_r")
                is_nutids_r.append(None)
        return is_nutids_r
            
    def correct(self, sentence, pos):
        self.pos = pos
        self.current_sentence = sentence
        words = prepare_sentence(sentence, lowercase=True)
        verbs_to_check = self.verbs_to_check(words, pos)
        should_be_nutids_r = self.should_be_nutids_r(words, verbs_to_check)
        is_nutids_r = self.is_verbs_nutids_r(words, verbs_to_check)
        errors = self.make_error_messages(words, should_be_nutids_r, is_nutids_r, verbs_to_check)
        return move_index_based_on_br(errors, sentence), verbs_to_check, self.buffer, self.edge_cases, should_be_nutids_r, [(words[i], self.pos[i][0]) for i in range(len(words))]
