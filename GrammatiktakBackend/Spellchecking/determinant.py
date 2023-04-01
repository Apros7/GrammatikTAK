from Utilities.utils import prepare_sentence, find_index

class determinantCorrector():
    """
    Rule based detector for finding the following errors:
     - en/et
     - den/det
    """
    
    def __init__(self) -> None:
        self.posible_corrections ={"den": "det", "det": "den", "en": "et", "et": "en"}
        self.posible_corrections_values = self.posible_corrections.values()
    
    def create_determinant_error_message(self, word_to_correct, noun, all_words_from_sentence, index_of_word_in_all_words) -> list:
        correct_word = self.posible_corrections[word_to_correct]
        gender = "fælleskøn" if word_to_correct[0] == "n" else "intetkøn"
        error_description = f"Der skal skrives '{correct_word}' foran {noun}, da {noun} er {gender}"
        previous_index = find_index(all_words_from_sentence, index_of_word_in_all_words, word_to_correct)
        wrong_word = word_to_correct
        right_word = correct_word.capitalize() if wrong_word[-1].isupper() else correct_word
        return [wrong_word, right_word, previous_index, error_description]

    def correct_determinants(self, sentence, pos_tag):
        words = prepare_sentence(sentence, lowercase=False, clean=True)
        nouns = [True if x[0] == "NOUN" else False for x in pos_tag]
        prev_det = [False] + [True if pos_tag[i-1][0] == "DET" else False for i in range(1, len(pos_tag))]
        error = [False] + [not (pos_tag[i][2]["Gender"] == pos_tag[i-1][2]["Gender"]) if nouns[i] and prev_det[i] else False for i in range(1, len(nouns))]
        error_messages = [self.create_determinant_error_message(words[i-1], words[i], words, i-1) for i in range(1, len(words)) if error[i] and words[i-1] in self.posible_corrections_values]
        return error_messages
