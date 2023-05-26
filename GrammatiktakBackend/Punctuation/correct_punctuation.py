import torch
from transformers import Trainer, BertTokenizer
import numpy as np
from Utilities.utils import prepare_sentence, find_index, move_index_based_on_br
from Utilities.error_handling import Error, ErrorList
from Utilities.model_utils import Dataset, load_model

PUNCTUATIONS_WITHOUT_COMMA = ".!?\";:"
PUNCTUATIONS_FULL_STOP = ".!?"
PUNCTUATIONS = "!\"#$%&'()*+,-./:;=?@[\]^_`{|}~"

model_path = "models/commaModel10"
model_left_padding = 15
model_right_padding = 10

# This class will predict punctuation and correct based on sentence
class PunctuationCorrector():
    def __init__(self) -> None:
        self.model = load_model(model_path)
        self.left_padding, self.right_padding = model_left_padding, model_right_padding
        self.tokenizer = BertTokenizer(vocab_file="models/vocab.txt", do_lower_case=False)
    
    def add_padding(self, words):
        return ["<pad>"]*self.left_padding + words + ["<pad>"]*self.right_padding

    # prepares dataset and get predictions
    def get_predictions(self, sentence) -> list:
        words = self.add_padding(prepare_sentence(sentence))
        if len(words) < self.left_padding:
            return [0]*len(words)
        test_data = [" ".join(words[i:i+self.left_padding+self.right_padding]) for i in range(len(words)-self.left_padding-self.right_padding)]
        test_data = [data.translate(str.maketrans("", "", PUNCTUATIONS)) for data in test_data]
        tokenized_data = self.tokenizer(test_data, padding=True, truncation=True)
        final_dataset = Dataset(tokenized_data)
        raw_predictions, _, _ = self.model.predict(final_dataset)
        final_predictions = np.argmax(raw_predictions, axis=1)
        return final_predictions

    # creates comma error message
    def create_comma_error_message(self, word_to_correct, all_words_from_sentence, index_of_word_in_all_words, remove) -> Error():
        error_description = f"Der skal ikke være komma efter '{word_to_correct[:-1]}'." if remove else f"Der skal være komma efter '{word_to_correct}'."
        error_type = "del_punc" if remove else "add_punc"
        previous_index = find_index(all_words_from_sentence, index_of_word_in_all_words, word_to_correct)
        if remove:
            wrong_word, right_word = word_to_correct, word_to_correct[:-1]
        else:
            wrong_word, right_word  = word_to_correct, word_to_correct + ","
        return Error(wrong_word, right_word, previous_index, error_description, error_type)
    
    # creates full stop error message
    def create_full_stop_error_message(self, word_to_correct, all_words_from_sentence, index_of_word_in_all_words) -> Error():
        error_description = f"Der skal være punktum efter '{word_to_correct}', da det er det sidste ord i sætningen."
        error_type = "add_punc"
        previous_index = find_index(all_words_from_sentence, index_of_word_in_all_words, word_to_correct)
        wrong_word, right_word  = word_to_correct, word_to_correct + "."
        return Error(wrong_word, right_word, previous_index, error_description, error_type)

    # find mistakes and makes errors
    # should be changed after model is retrained to character level
    def find_comma_mistakes(self, predictions, words) -> ErrorList:
        # get relevant lists:
        # every words is checked but the last one
        checked_words = [words[i] for i in range(len(words)-1)]
        predicted_comma = [True if predictions[i] == 1 else False for i in range(len(checked_words))]
        already_punctuated = [True if checked_words[i][-1] in PUNCTUATIONS_WITHOUT_COMMA else False for i in range(len(checked_words))]
        already_comma = [True if checked_words[i][-1] == "," else False for i in range(len(checked_words))]
        # where there should be a comma but isnt
        error_new_comma = [True if predicted_comma[i] and (not already_punctuated[i]) and (not already_comma[i]) else False for i in range(len(predicted_comma))]
        error_messages_new_comma = [self.create_comma_error_message(checked_words[i], words, i, False) for i in range(len(checked_words)) if error_new_comma[i]]
        # where there should not be a comma but is
        error_remove_comma = [True if (not predicted_comma[i]) and (not already_punctuated[i]) and already_comma[i] else False for i in range(len(predicted_comma))]
        error_messages_remove_comma = [self.create_comma_error_message(checked_words[i], words, i, True) for i in range(len(checked_words)) if error_remove_comma[i]]
        comma_errors = ErrorList(error_messages_new_comma + error_messages_remove_comma)
        final_errors = self.ignore_mistakes_in_ner_objects(comma_errors)
        return final_errors

    # finds full stop mistakes and makes errors
    # errors are no full stop at end of sentence
    def find_full_stop_mistakes(self, sentence, prepared_words) -> ErrorList:
        words_for_every_sentence = prepare_sentence(sentence, split_sentences=True)
        full_stop_error = [True if word[-1] not in PUNCTUATIONS_FULL_STOP and i == len(sent)-1 else False for sent in words_for_every_sentence for i, word in enumerate(sent)]
        error_messages_full_stop = [self.create_full_stop_error_message(prepared_words[i], prepared_words, i) for i in range(len(prepared_words)) if full_stop_error[i]]
        return ErrorList(error_messages_full_stop)

    def ignore_mistakes_in_ner_objects(self, mistakes: ErrorList):
        mistakes_list = mistakes.to_list(include_type=True)
        ner_indexes = [index for (name, index) in self.ner_tags]

        filtered_mistakes = []
        for mistake in mistakes_list:
            mistake_indexes = mistake[2]
            if not any(start <= mistake_indexes[0] <= end or start <= mistake_indexes[1] <= end for (start, end) in ner_indexes):
                filtered_mistakes.append(mistake)

        return ErrorList(filtered_mistakes)

    # this model should be retrained to used character based inputs
    # instead of word based inputs
    # this is the function to call when error messages are needed
    def correct_punctuation(self, sentence, ner_tags):
        self.ner_tags = ner_tags
        predictions = self.get_predictions(sentence)
        words = prepare_sentence(sentence, lowercase=False)
        comma_mistakes = self.find_comma_mistakes(predictions, words)
        full_stop_mistakes = self.find_full_stop_mistakes(sentence, words)
        return move_index_based_on_br(comma_mistakes + full_stop_mistakes, sentence)
