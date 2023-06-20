import pickle
import pandas as pd
import os
import torch
from transformers import Trainer, BertTokenizer


os.chdir("/Users/lucasvilsen/Desktop/GrammatikTAK/")

training_set = pd.read_csv("Datasets/EuroparlNutidsr_trainset_verbs.csv", sep=";")
print("Loaded data")

testset = list(training_set["comment_text"].values)
true_labels = list(training_set["label"].values)

tokenizer = BertTokenizer.from_pretrained('Maltehb/danish-bert-botxo')

print("Loaded model")

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


def tokenize_sentences(sentences):
    X_tokenized = tokenizer(sentences, padding=True, truncation=True)
    return X_tokenized

tokenized = tokenize_sentences(testset)
print("Tokenized data")

import pickle
with open("FineTuneModels/tokenized.pickle", "wb") as f:
    pickle.dump(tokenized, f)
print("Saved tokenized data")