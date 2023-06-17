import sys
sys.path.append("/Users/lucasvilsen/Desktop/GrammatikTAK/GrammatiktakBackend/")
from Utilities.utils import prepare_sentence, move_index_based_on_br, IndexFinder
from Utilities.error_handling import Error, ErrorList

class ExcessiveSpacesCorrector():
    def __init__(self) -> None: pass

    def create_full_stop_error_message(self, number_of_spaces, index_of_word_in_all_words) -> Error():
        error_description = f"Det ser ud til, at du har sat {number_of_spaces} mellemrum i her."
        error_type = "spaces"
        previous_index = self.index_finder.find_index(index_of_word_in_all_words, " "*number_of_spaces)
        wrong_word, right_word  = " "*number_of_spaces, " "
        return Error(wrong_word, right_word, previous_index, error_description, error_type)

    def correct(self, sentence, pos_tags, ner_tags, index_finder):
        errors = ErrorList()
        self.index_finder = index_finder
        words = sentence.split(" ")
        print(words)
        for i in range(len(words)):
            if words[i-1] == "": continue
            if words[i] == "":
                number_of_spaces = 2
                for j in range(i+1, len(words)):
                    if words[j] == "":
                        number_of_spaces += 1
                    else:
                        break
                print(number_of_spaces)
                errors.append(self.create_full_stop_error_message(number_of_spaces, i))
        return errors.to_list(finalize=True)

sentence = "hej jeg hedder lucas. hej jeg hedder  lucas. hej jeg hedder      lucas.  hej jeg hedder lucas.  "
index_finder = IndexFinder(sentence)
corrector = ExcessiveSpacesCorrector()
print(*corrector.correct(sentence=sentence, index_finder=index_finder), sep="\n")