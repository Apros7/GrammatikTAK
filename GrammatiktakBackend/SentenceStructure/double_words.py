
from Utilities.utils import prepare_sentence, move_index_based_on_br
from Utilities.error_handling import Error, ErrorList

import pickle

class DoubleWordsChecker():
    """
    Corrects double words in a sentence
    """
    def __init__(self): self.composite_dict = pickle.load(open("Datasets/composite_dict.pickle", "rb"))
    def cut_ouf_indexes(self, lst, indexes_to_cut_out): return [lst[i] for i in range(len(lst)) if i not in indexes_to_cut_out]
    def word_in_ner_tags(self, word_index, ner_tags): return any([word_index == ner_index for ner_index in ner_tags])

    # other error_type??

    def create_double_word_error_message(self, wrong_word, all_words_from_sentence, index_of_word_in_all_words):
        error_type = "doublewords"
        correct_word = wrong_word.split()[0]
        error_description = f"Det ser ud til, at du er kommet til at skrive '{correct_word}' {len(wrong_word.split())} gange."
        previous_index = self.index_finder.find_index(index_of_word_in_all_words, wrong_word)
        return Error(wrong_word, correct_word, previous_index, error_description, error_type)

    def create_composite_error_message(self, wrong_word, correct_word, index_of_word_in_all_words):
        error_type = "doublewords"
        error_description = f"Det ligner, at du har skrevet '{wrong_word}' forkert. Den rigtige måde er: '{correct_word}'."
        previous_index = self.index_finder.find_index(index_of_word_in_all_words, wrong_word)
        return Error(wrong_word, correct_word, previous_index, error_description, error_type)

    def push_ner_tags(self, index, ner_tags, amount):
        new_tags = []
        for tag in ner_tags:
            if index == tag: continue
            if tag > index: new_tags.append(tag + amount)
            else: new_tags.append(tag)
        return new_tags

    def correct_double_words(self, words, ner_tags, pos_tags):
        """
        Check if this hard-coding is correct: Is "så" the only word that will show up after each other?
        Needs refactoring
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
                ner_tags = self.push_ner_tags(i, ner_tags, -len(temp) + 1)
                for k in range(i+1, j):
                    self.index_finder.add_index(k, "")
        new_words = self.cut_ouf_indexes(words, indexes_to_cut_out)     
        pos_tags = self.cut_ouf_indexes(pos_tags, indexes_to_cut_out) 
        return errors, new_words, ner_tags, pos_tags
    
    def check_composite_words(self, words, ner_tags, pos_tags, number_of_words_at_a_time):
        errors = ErrorList()
        for i in range(len(words) - number_of_words_at_a_time - 1):
            if self.word_in_ner_tags(i, ner_tags): continue
            true_words = " ".join(words[i:i+number_of_words_at_a_time])
            word = true_words.replace(" ", "")
            if word in self.composite_dict:
                if true_words == self.composite_dict[word][0]:
                    continue
                errors.append(self.create_composite_error_message(true_words, self.composite_dict[word][0], i))
                correct_words = self.composite_dict[word][0].split()
                for j in range(len(correct_words)):
                    index = i + j
                    if index < i + number_of_words_at_a_time:
                        words[index] = correct_words[j]
                        pos_tags[index] = self.composite_dict[word][1][j]
                    else:
                        words.insert(index, correct_words[j])
                        pos_tags.insert(index, self.composite_dict[word][1][j])
                        ner_tags = self.push_ner_tags(index, ner_tags, 1)
                        self.index_finder.add_index(index, correct_words[j], add=True)
                if number_of_words_at_a_time > len(correct_words):
                    for j in range(number_of_words_at_a_time - len(correct_words)):
                        index = i + j + len(correct_words)
                        words.pop(index)
                        pos_tags.pop(index)
                        ner_tags = self.push_ner_tags(index, ner_tags, -1)
                        self.index_finder.add_index(index, "")
        return errors, words, ner_tags, pos_tags

    def correct_composite_words(self, words, ner_tags, pos_tags):
        all_errors = ErrorList()
        for i in range(1, 4):
            self.index_finder.freeze() # Needs to freeze because next self.check_composite_words works on return value from prev state, which could have been changed
            errors, words, ner_tags, pos_tags = self.check_composite_words(words, ner_tags, pos_tags, 1)
            all_errors += errors
        return all_errors, words, ner_tags, pos_tags

    def correct(self, sentence, pos_tags, ner_tags, index_finder):
        self.index_finder = index_finder
        words = prepare_sentence(sentence, lowercase=False)
        double_word_errors, words, ner_tags, pos_tags = self.correct_double_words(words, ner_tags, pos_tags)
        composite_errors, words, ner_tags, pos_tags = self.correct_composite_words(words, ner_tags, pos_tags)
        return move_index_based_on_br(double_word_errors + composite_errors, sentence), (" ".join(words), pos_tags, ner_tags)