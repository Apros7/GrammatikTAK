from transformers import AutoTokenizer, AutoModel
import torch
from torch.utils.data import Dataset, DataLoader
from datasets import load_metric
import pandas as pd
from sklearn.model_selection import train_test_split
import time
import numpy as np
from transformers import TrainingArguments, Trainer, BertForSequenceClassification
import os
from sklearn.metrics import accuracy_score
from tqdm import tqdm
from transformers import TextClassificationPipeline

os.chdir("/Users/lucasvilsen/Desktop/GrammatikTAK/Datasets")

tokenizer = AutoTokenizer.from_pretrained("Geotrend/distilbert-base-da-cased")

# df = pd.read_csv("SentToLabel_15-5_Revisited.csv", sep=";")
# print(len(df))

# df_train = df[:1000000] # should not be active
# df_test = df[25000000:26000000]

df_train = pd.read_csv("SentToLabel_15-5_Revisited_train.csv", sep=";")
df_test = pd.read_csv("SentToLabel_15-5_Revisited_test.csv", sep=";")
df_train = df_train[:10]
df_test = df_test[:100000]

# df_train.to_csv("SentToLabel_15-5_Revisited_train.csv", sep=";")
# df_test.to_csv("SentToLabel_15-5_Revisited_test.csv", sep=";")

data_train = df_train["data"].to_list()
labels_train = df_train["label"].to_list()

data_test = df_test["data"].to_list()
labels_test = df_test["label"].to_list()

batch_size = 32

class CustomDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels=None, batch_size=16):
        self.encodings = encodings
        self.labels = labels
        self.batch_size = batch_size

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        if self.labels:
            item["labels"] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.encodings["input_ids"])

os.chdir("/Users/lucasvilsen/Desktop")

device = "mps"
torch.device(device)
model = torch.load("commaDistilBERT1", map_location=torch.device('cpu'))
model.to(device)
model.eval()
trainer = Trainer(model)

pipe = TextClassificationPipeline(model=model, tokenizer=tokenizer, return_all_scores=True)

def evaluate_model(model, data, labels):
    with torch.no_grad():
        tokenized_data = tokenizer(data, padding=True, truncation=True)
        final_dataset = CustomDataset(tokenized_data)
        raw_predictions, _, _ = model.predict(final_dataset)
        true_predictions = np.argmax(raw_predictions, axis=1)
        accuracy = accuracy_score(labels, true_predictions)
    return accuracy

train_accuracy = evaluate_model(trainer, data_train, labels_train)
print(f"Train Accuracy: {train_accuracy:.6f}")

test_accuracy = evaluate_model(trainer, data_test, labels_test)
print(f"Test Accuracy: {test_accuracy:.6f}")
