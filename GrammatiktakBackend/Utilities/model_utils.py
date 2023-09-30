import torch
from transformers import Trainer, DistilBertForSequenceClassification, DistilBertTokenizerFast
import string
import numpy as np

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

def load_model(model_path):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    torch.device(device)
    punctuation_model = torch.load(model_path, map_location=torch.device(device))
    punctuation_model.eval()
    punctuation_model.to(device)
    punctuation_trainer = Trainer(punctuation_model)
    return punctuation_trainer

class DistilBertForPunctuation():
    """
    Loads and gives functionality to easily go from data to predictions
    """
    def __init__(self) -> None:
        self.trainer = self.load_trainer()
        self.tokenizer = DistilBertTokenizerFast.from_pretrained("Geotrend/distilbert-base-da-cased")
        self.padding_left, self.padding_right = 15, 5

    def load_trainer(self):
        # not tested. Maybe us os.chdir()
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        torch.device(device)
        model = DistilBertForSequenceClassification.from_pretrained("commaDistilBERTcorrect")
        model.eval()
        model.to(device)
        trainer = Trainer(model)
        return trainer

    def clean(self, data):
        TRANSLATION_TABLE_WITHOUT_COMMA_AND_PUNC = str.maketrans('', '', string.punctuation.replace(",", "").replace(".", "")) 
        cleaned_lines = [line.replace(" -", ",").lower() for line in data if len(line.translate(TRANSLATION_TABLE_WITHOUT_COMMA_AND_PUNC).strip()) > 0]
        lines_with_comma = [line.translate(TRANSLATION_TABLE_WITHOUT_COMMA_AND_PUNC).strip().replace("  ", " ") for line in cleaned_lines]
        return lines_with_comma

    def get_dataset(self, data : list):
        cleaned_lines = self.clean(data)
        lines_with_padding = [self.padding_left * ["<PAD>"] + line.split() + self.padding_right * ["<PAD>"] for line in cleaned_lines]
        cleaned_dataset = []

        for i in range(len(lines_with_padding)):
            for j in range(len(lines_with_padding[i])-(self.padding_left+self.padding_right)+1):
                sample = lines_with_padding[i][j:j+self.padding_left+self.padding_right]
                cleaned_dataset.append((" ".join(sample)).replace(",", "").replace(".", ""))

        return cleaned_dataset

    def get_predictions(self, data : list):
        dataset = self.get_dataset(data)
        tokenized_data = self.tokenizer(data, padding=True, truncation=True)
        final_dataset = Dataset(tokenized_data)
        raw_predictions, _, _ = self.trainer.predict(final_dataset)
        true_predictions = np.argmax(raw_predictions, axis=1)
        return true_predictions
    