import sys
sys.path.append("/Users/lucasvilsen/Desktop/GrammatikTAK/GrammatiktakBackend/")
from Utilities.utils import prepare_sentence, move_index_based_on_br, IndexFinder, check_if_index_is_correct
from Utilities.error_handling import Error, ErrorList

class ExcessiveSpacesCorrector():
    def __init__(self) -> None: pass

    def find_indexes(self, index, words, number_of_spaces):
        """
        Indexes works on spaces and not words, so therefore needs to be corrected.
        """
        first_index = sum([len(word) for word in words[:index]]) + sum([1 for word in words[:index]])
        return [first_index - 1, first_index + number_of_spaces - 1]

    def create_full_stop_error_message(self, number_of_spaces, index_of_word_in_all_words, words) -> Error():
        error_description = f"Det ser ud til, at du har sat {number_of_spaces} mellemrum i her."
        error_type = "spaces"
        indexes = self.find_indexes(index_of_word_in_all_words, words, number_of_spaces)
        wrong_word, right_word  = " "*number_of_spaces, " "
        return Error(wrong_word, right_word, indexes, error_description, error_type)

    def correct(self, sentence, pos_tags, ner_tags, index_finder):
        errors = ErrorList()
        self.index_finder = index_finder
        words = sentence.split(" ")
        for i in range(len(words)):
            if words[i-1] == "": continue
            if words[i] == "":
                number_of_spaces = 2
                for j in range(i+1, len(words)):
                    if words[j] == "":
                        number_of_spaces += 1
                    else:
                        break
                if all([words[k] == "" for k in range(0, i+1)]) or all([words[k] == "" for k in range(i, len(words))]):
                    number_of_spaces -= 1
                if number_of_spaces < 2: continue
                errors.append(self.create_full_stop_error_message(number_of_spaces, i, words))
        return move_index_based_on_br(errors, sentence), (" ".join(words), pos_tags, ner_tags)

if __name__ == "__main__":
    sentence = "  hej jeg hedder lucas. hej jeg hedder  lucas. hej jeg hedder      lucas.  hej jeg hedder lucas.  "
    index_finder = IndexFinder(sentence)
    corrector = ExcessiveSpacesCorrector()
    print(*corrector.correct(sentence, None, None, index_finder=index_finder)[0].to_list(finalize=True), sep="\n")
    check_if_index_is_correct(corrector.correct(sentence, None, None, index_finder=index_finder)[0].to_list(), sentence)