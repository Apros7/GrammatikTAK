import torch
from transformers import Trainer, DistilBertForSequenceClassification
import string

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

def load_distil_bert():
    # Function not tested
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    torch.device(device)
    model = DistilBertForSequenceClassification.from_pretrained("commaDistilBERTcorrect")
    model.eval()
    model.to(device)
    trainer = Trainer(model)
    return trainer

def distil_bert_datamaker(lines : list):
    # Lines should be list of strings
    # Function not tested
    TRANSLATION_TABLE_WITH_COMMA = str.maketrans('', '', string.punctuation)
    TRANSLATION_TABLE_WITHOUT_COMMA = str.maketrans('', '', string.punctuation.replace(",", "").replace(".", "")) 

    cleaned_lines = [line.replace(" -", ",").lower() for line in lines if len(line.translate(TRANSLATION_TABLE_WITHOUT_COMMA).strip()) > 0]
    lines_with_comma = [line.translate(TRANSLATION_TABLE_WITHOUT_COMMA).strip().replace("  ", " ") for line in cleaned_lines]

    PADDING_LEFT = 15
    PADDING_RIGHT = 5

    lines_with_padding = [PADDING_LEFT * ["<PAD>"] + line.split() + PADDING_RIGHT * ["<PAD>"] for line in lines_with_comma]
    cleaned_dataset = []

    for i in range(len(lines_with_padding)):
        for j in range(len(lines_with_padding[i])-(PADDING_LEFT+PADDING_RIGHT)+1):
            sample = lines_with_padding[i][j:j+PADDING_LEFT+PADDING_RIGHT]
            if sample[PADDING_LEFT-1][-1] == ",": middle_word_punc = 1
            elif sample[PADDING_LEFT-1][-1] == ".": middle_word_punc = 2
            else: middle_word_punc = 0
            cleaned_dataset.append((" ".join(sample)).replace(",", "").replace(".", ""))

    return cleaned_dataset