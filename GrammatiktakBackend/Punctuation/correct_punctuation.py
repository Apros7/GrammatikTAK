import torch
from transformers import Trainer, BertTokenizer
import numpy as np
from Utilities.utils import prepare_sentence, find_index, move_index_based_on_br

PUNCTUATIONS_WITHOUT_COMMA = ".!?\";:"
PUNCTUATIONS = ".!?"

# used to create torch dataset for predictions
class Dataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels=None):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        if self.labels:
            item["labels"] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.encodings["input_ids"])

# loads model and returns trainer object
def load_model():

    # punctuation model, padding and scope should match model and dataset
    # should have padding so that every word except the last is checked
    # else the logic in finding "find_comma_mistakes" needs to be changed
    punctuation_model = torch.load("commaModel2", map_location=torch.device('mps'))
    scope = 6
    padding = int(scope/2-1)

    punctuation_model.eval()
    punctuation_trainer = Trainer(punctuation_model)
    return punctuation_trainer, scope, padding

device = "mps"
torch.device(device)

# This class will predict punctuation and correct based on sentence
class PunctuationCorrector():
    def __init__(self) -> None:
        self.model, self.scope, self.padding = load_model()
        self.tokenizer = BertTokenizer.from_pretrained("Maltehb/danish-bert-botxo")
    
    def add_padding(self, words):
        return ["<PAD>"]*self.padding + words + ["<PAD>"]*self.padding

    # prepares dataset and get predictions
    def get_predictions(self, sentence) -> list:
        words = self.add_padding(prepare_sentence(sentence))
        if len(words) < self.scope:
            return [0]*len(words)
        test_data = [" ".join(words[i:i+self.scope]).strip(PUNCTUATIONS_WITHOUT_COMMA).strip(",") for i in range(len(words)-self.scope-1+self.padding)]
        tokenized_data = self.tokenizer(test_data, padding=True, truncation=True, max_length=512)
        final_dataset = Dataset(tokenized_data)
        raw_predictions, _, _ = self.model.predict(final_dataset)
        final_predictions = np.argmax(raw_predictions, axis=1)
        return final_predictions

    # creates comma error message
    def create_comma_error_message(self, word_to_correct, all_words_from_sentence, index_of_word_in_all_words, remove) -> list:
        error_description = f"Der skal ikke være komma efter '{word_to_correct[:-1]}'." if remove else f"Der skal være komma efter '{word_to_correct}'."
        previous_index = find_index(all_words_from_sentence, index_of_word_in_all_words, word_to_correct)
        if remove:
            wrong_word, right_word = word_to_correct, word_to_correct[:-1]
        else:
            wrong_word, right_word  = word_to_correct, word_to_correct + ","
        return [wrong_word, right_word, previous_index, error_description]
    
    # creates full stop error message
    def create_full_stop_error_message(self, word_to_correct, all_words_from_sentence, index_of_word_in_all_words) -> list:
        error_description = f"Der skal være punktum efter '{word_to_correct}', da det er det sidste ord i sætningen."
        previous_index = find_index(all_words_from_sentence, index_of_word_in_all_words, word_to_correct)
        wrong_word, right_word  = word_to_correct, word_to_correct + "."
        return [wrong_word, right_word, previous_index, error_description]

    # find mistakes and makes errors
    # should be changed after model is retrained to character level
    def find_comma_mistakes(self, predictions, words) -> list:
        # get relevant lists:
        # every words is checked but the last one
        checked_words = [words[i] for i in range(len(words)-1)]
        predicted_comma = [True if predictions[i] == 1 else False for i in range(len(checked_words))]
        already_punctuated = [True if checked_words[i][-1] in PUNCTUATIONS_WITHOUT_COMMA else False for i in range(len(checked_words))]
        already_comma = [True if checked_words[i][-1] == "," else False for i in range(len(checked_words))]
        # where there should be a comma but isnt
        error_new_comma = [True if predicted_comma[i] and (not already_punctuated[i]) and (not already_comma[i]) else False for i in range(len(predicted_comma))]
        error_messages_new_comma = [self.create_comma_error_message(checked_words[i], words, i+1, False) for i in range(len(checked_words)) if error_new_comma[i]]
        # where there should not be a comma but is
        error_remove_comma = [True if (not predicted_comma[i]) and (not already_punctuated[i]) and already_comma[i] else False for i in range(len(predicted_comma))]
        error_messages_remove_comma = [self.create_comma_error_message(checked_words[i], words, i+1, True) for i in range(len(checked_words)) if error_remove_comma[i]]
        return error_messages_new_comma + error_messages_remove_comma

    # finds full stop mistakes and makes errors
    # errors are no full stop at end of sentence
    def find_full_stop_mistakes(self, sentence, prepared_words) -> list:
        words_for_every_sentence = prepare_sentence(sentence, split_sentences=True)
        full_stop_error = [True if word[-1] not in PUNCTUATIONS and sent[-1] == word else False for sent in words_for_every_sentence for word in sent]
        error_messages_full_stop = [self.create_full_stop_error_message(prepared_words[i], prepared_words, i) for i in range(len(prepared_words)) if full_stop_error[i]]
        return error_messages_full_stop


    # this model should be retrained to used character based inputs
    # instead of word based inputs
    # this is the function to call when error messages are needed
    def correct_punctuation(self, sentence):
        predictions = self.get_predictions(sentence)
        words = prepare_sentence(sentence, lowercase=False)
        comma_mistakes = self.find_comma_mistakes(predictions, words)
        full_stop_mistakes = self.find_full_stop_mistakes(sentence, words)
        return move_index_based_on_br(comma_mistakes + full_stop_mistakes, sentence)
