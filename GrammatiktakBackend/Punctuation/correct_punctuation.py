import torch
from transformers import pipeline, Trainer, BertTokenizer
import numpy as np

PUNCTUATIONS = ".,!?\";:"

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
    punctuation_model = torch.load("modelCombined2")
    punctuation_model.eval()
    punctuation_trainer = Trainer(punctuation_model)
    return punctuation_trainer

# This class will predict punctuation and correct based on sentence
class PunctuationCorrector():
    def __init__(self) -> None:
        self.model = load_model()
        self.tokenizer = BertTokenizer.from_pretrained("Maltehb/danish-bert-botxo")
    
    # prepares function for prediction
    # should be useless after model is retrained
    def prepare_sentence(self, sentence) -> str:
        return sentence.replace("<br>", " ").lower().split()
    
    # prepares dataset and get predictions
    def get_predictions(self, sentence) -> list:
        words = self.prepare_sentence(sentence)
        test_data = [" ".join(words[i:i+4]) for i in range(len(words)-3)]
        tokenized_data = self.tokenizer(test_data, padding=True, truncation=True, max_length=512)
        final_dataset = Dataset(tokenized_data)
        raw_predictions, _, _ = self.model.predict(final_dataset)
        final_predictions = np.argmax(raw_predictions, axis=1)
        return final_predictions, words

    # creates comma error message
    def create_comma_error_message(self, word_to_correct, all_words_from_sentence, index_of_word_in_all_words) -> list:
        index_of_word_to_correct = sum([len(word) for word in all_words_from_sentence[:index_of_word_in_all_words]]) + len(all_words_from_sentence)-1
        error_description = f"Der skal være komma efter '{word_to_correct}'."
        previous_index = [index_of_word_to_correct, index_of_word_to_correct + len(word_to_correct)]
        new_index = [previous_index[0], previous_index[1] + 1]
        return [word_to_correct, word_to_correct + ",", previous_index, new_index, error_description]

    # find mistakes and makes errors
    # should be changed after model is retrained to character level
    def find_mistakes(self, predictions, words) -> str:
        checked_words = [words[i+1] for i in range(len(words)-3)]
        predicted_comma = [True if predictions[i] == 2 else False for i in range(len(predictions))]
        already_punctuated = [True if checked_words[-1] in PUNCTUATIONS else False for i in range(len(checked_words))]
        error_messages = [True if predicted_comma[i] and not already_punctuated[i] else False for i in range(len(predicted_comma))]
        return [self.create_comma_error_message(checked_words[i], words, i+1) for i in range(len(checked_words)) if error_messages[i]]

    # this model should be retrained to used character based inputs
    # instead of word based inputs
    # this is the function to call when error messages are needed
    def correct_punctuation(self, sentence):
        predictions, words = self.get_predictions(sentence)
        mistakes = self.find_mistakes(predictions, words)
        return mistakes
