
from Utilities.utils import prepare_sentence, move_index_based_on_br, get_pos_without_information
from Utilities.error_handling import Error, ErrorList

class MissingFoundationChecker():
    """
    Based on logic
    Hvis VERB - PRON - VERB, så mangler PRON først.
    Skal kun virke, hvis punktum foran eller første ord.
    """

    def __init__(self):
        print("Loading Foundation checker...")

    def create_error_message(self, wrong_word, correct_word, all_words_from_sentence, index_of_word_in_all_words) -> list:
        error_type = "foundation"
        error_description = "Det ligner, at der mangler et subjekt i denne sætning."
        prev_index = self.index_finder.find_index(all_words_from_sentence, index_of_word_in_all_words, wrong_word)
        return Error(wrong_word, correct_word, prev_index, error_description, error_type)

    # def push_pos_indexes(self, pos, index):
    #     for i in range(index, len(pos) - 1):
    #         pos[i][1] = [pos[i][1][0] + 4, pos[i][1][1] + 4]
    #     return pos

    def get_foundation_errors(self, words, pos_tags):
        pos = get_pos_without_information(pos_tags)
        indexes_to_check = [0] + [i for i in range(1, len(words)) if words[i-1][-1] in ".?!"]
        new_words = words
        new_pos = pos_tags
        errors = ErrorList()
        for index in indexes_to_check:
            if index + 3 > len(words): break
            if pos[index:index+3] != ["VERB", "PRON", "VERB"]: continue
            errors.append(self.create_error_message(words[index], "Jeg " + words[index], words, index))
            new_words = new_words[:index] + ["Jeg"] + new_words[index:]
            indexes = self.index_finder.find_index(words, index, words[index])
            new_pos = new_pos[:index] + [["PRON", [indexes[0], indexes[0]], {}]] + new_pos[index:]
            self.index_finder.add_index(index)
        return errors, (new_words, new_pos)

    def correct(self, sentence, pos_tags, ner_tags, index_finder):
        self.index_finder = index_finder
        words = prepare_sentence(sentence)
        errors, (new_words, new_pos) = self.get_foundation_errors(words, pos_tags)
        return move_index_based_on_br(errors, sentence), (" ".join(new_words), new_pos, ner_tags), index_finder