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

    def find_spaces_errors(self, sentence, pos_tags, ner_tags, number_of_spaces_corrected):
        errors = ErrorList()
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
                if i-number_of_spaces > 0:
                    ner_tags = self.adjust_ner_tags(-number_of_spaces + 1, ner_tags, i-number_of_spaces_corrected)
                    number_of_spaces_corrected += number_of_spaces - 1
        errors = self.forget_beginning_errors(errors)
        return move_index_based_on_br(errors, sentence), (" ".join(words), pos_tags, ner_tags)

    def forget_beginning_errors(self, errors): return ErrorList([error for error in errors if error.indexes[0] >= 0])
    def adjust_ner_tags(self, adjust_with, ner_tags, index): return [tag + adjust_with if tag >= index else tag for tag in ner_tags]

    def beginning_spaces_errors(self, sentence, pos_tags, ner_tags):
        i = 0
        words = prepare_sentence(sentence)
        if len(words) < 1: return None
        while sentence[i] == " " and i < len(sentence):
            i += 1
        if i > 0: error = Error(i*" ", "", [0, i], f"Det ser ud til, at du har sat {i} mellemrum foran '{words[0]}'", "spaces")
        else: error = None
        ner_tags = self.adjust_ner_tags(-i, ner_tags, 0)
        return move_index_based_on_br(ErrorList([error]), sentence), (sentence[i:], pos_tags, ner_tags), i

    def correct(self, sentence, pos_tags, ner_tags, index_finder):
        self.index_finder = index_finder
        begin_error, (sentence, pos_tags, ner_tags), number_of_spaces = self.beginning_spaces_errors(sentence, pos_tags, ner_tags)
        errors, (sentence, pos_tags, ner_tags) = self.find_spaces_errors(sentence, pos_tags, ner_tags, number_of_spaces)
        print("Final ner_tags", ner_tags)
        return errors + begin_error, (sentence, pos_tags, ner_tags)

if __name__ == "__main__":
    sentence = "  hej jeg hedder lucas. hej jeg hedder  lucas. hej jeg hedder      lucas.  hej jeg hedder lucas.  "
    index_finder = IndexFinder(sentence)
    corrector = ExcessiveSpacesCorrector()
    print(*corrector.correct(sentence, None, None, index_finder=index_finder)[0].to_list(finalize=True), sep="\n")
    check_if_index_is_correct(corrector.correct(sentence, None, None, index_finder=index_finder)[0].to_list(), sentence)