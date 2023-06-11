
from Utilities.utils import prepare_sentence, move_index_based_on_br
from Utilities.error_handling import Error, ErrorList

class DoubleWordsChecker():
    """
    Corrects double words in a sentence
    Corrects composite words
    """
    def __init__(self):
        pass

    def create_double_word_error_message(self, wrong_word, all_words_from_sentence, index_of_word_in_all_words):
        error_type = "spellcheck"
        correct_word = wrong_word.split()[0]
        error_description = f"Det ser ud til, at du er kommet til at skrive '{correct_word}' {len(wrong_word.split())} gange."
        previous_index = self.index_finder.find_index(all_words_from_sentence, index_of_word_in_all_words, wrong_word)
        return Error(wrong_word, correct_word, previous_index, error_description, error_type)

    def cut_ouf_indexes(self, words, indexes_to_cut_out):
        return [words[i] for i in range(len(words)) if i not in indexes_to_cut_out]

    def pull_ner_tags_back(self, index, ner_tags, amount):
        new_tags = []
        for tag in ner_tags:
            if index == tag: continue
            if tag > index: new_tags.append(tag - amount)
            else: new_tags.append(tag)
        return new_tags

    def correct_double_words(self, words, ner_tags):
        """
        Check if this hard-coding is correct: Is "så" the only word that will show up after each other?
        """
        indexes_to_cut_out = []
        errors = ErrorList()
        for i in range(len(words)):
            if i > 0 and words[i] == words[i-1]:
                continue
            j = i
            temp = []
            while j < len(words) and words[i] == words[j]:
                temp.append(words[j])
                j += 1
            if len(temp) > 1 and words[i].lower() != "så":
                errors.append(self.create_double_word_error_message(" ".join(temp), words, i))
                indexes_to_cut_out.extend(range(i+1, j))
                ner_tags = self.pull_ner_tags_back(i, ner_tags, len(temp) - 1)
                characters_added_to_sentence = -len(" ".join(temp)) + len(temp[0]) + 1
                self.index_finder.add_index_list(list(range(i+1, j)), effect = characters_added_to_sentence)
        new_words = self.cut_ouf_indexes(words, indexes_to_cut_out)      
        return errors, new_words, ner_tags

    def correct_composite_words(self, words):
        pass

    def correct(self, sentence, pos_tags, ner_tags, index_finder):
        self.index_finder = index_finder
        words = prepare_sentence(sentence, lowercase=False)
        errors, words, ner_tags = self.correct_double_words(words, ner_tags)
        return move_index_based_on_br(errors, sentence), (" ".join(words), pos_tags, ner_tags), index_finder