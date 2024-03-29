
from Utilities.utils import prepare_sentence, move_index_based_on_br, get_pos_without_information
from Utilities.error_handling import Error, ErrorList

import pickle

class MissingFoundationChecker():
    """
    Based on logic
    Hvis VERB - PRON - VERB, så mangler PRON først.
    Skal kun virke, hvis punktum foran eller første ord.
    """

    def __init__(self):
        print("Loading Foundation checker...")
        self.stem_dict = pickle.load(open("Datasets/VbStemDict.pickle", "rb"))

    def create_error_message(self, wrong_word, correct_word, all_words_from_sentence, index_of_word_in_all_words) -> list:
        error_type = "foundation"
        error_description = "Det ligner, at der mangler et subjekt i denne sætning. Måske kan du indsætte 'Jeg'?"
        prev_index = self.index_finder.find_index(index_of_word_in_all_words, wrong_word)
        return Error(wrong_word, correct_word, prev_index, error_description, error_type)

    def push_ner_tags(self, index, ner_tags):
        return [tag + 1 if tag >= index else tag for tag in ner_tags]

    def get_foundation_errors(self, words, pos_tags, ner_tags):
        pos = get_pos_without_information(pos_tags)
        indexes_to_check = [0] + [i for i in range(1, len(words)) if words[i-1][-1] in ".?!"]
        new_words = words
        new_pos = pos_tags
        errors = ErrorList()
        foundations_added = 0
        for index in indexes_to_check:
            if index + 3 > len(words): break
            if pos[index:index+3] != ["VERB", "PRON", "VERB"]: continue
            if words[index].lower() not in self.stem_dict: continue
            word_to_add = "Jeg"
            errors.append(self.create_error_message(words[index], word_to_add + " " + words[index].lower(), words, index))
            new_words = new_words[:index+foundations_added] + [word_to_add] + [new_words[index+foundations_added].lower()] + new_words[index+1+foundations_added:]
            indexes = self.index_finder.find_index(index, words[index])
            new_pos = new_pos[:index+foundations_added] + [["PRON", [indexes[0], indexes[0]], {}]] + new_pos[index+foundations_added:]
            foundations_added += 1
            ner_tags = self.push_ner_tags(index, ner_tags)
            self.index_finder.add_index(index, "Jeg", add=True)
        return errors, (new_words, new_pos, ner_tags)

    def correct(self, sentence, pos_tags, ner_tags, index_finder):
        self.index_finder = index_finder
        words = prepare_sentence(sentence, lowercase=False)
        errors, (new_words, new_pos, ner_tags) = self.get_foundation_errors(words, pos_tags, ner_tags)
        return move_index_based_on_br(errors, sentence), (" ".join(new_words), new_pos, ner_tags)