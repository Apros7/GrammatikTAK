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

# scp Desktop/europarl-v7.da-en.da fsuser@87.120.210.92:/home/fsuser/
# pip3 install accelerate -U
# pip3 install datasets scikit-learn transformers pandas
# Desktop/GrammatikTAK/FineTuneModels/CommaModels/DistilBERTSentToLabel.py

tokenizer = AutoTokenizer.from_pretrained("Geotrend/distilbert-base-da-cased")

## CHANGE THIS ##
# os.chdir("/Users/lucasvilsen/Desktop/GrammatikTAK/Datasets")
# df = pd.read_csv("SentToLabel_15-5_Revisited_small.csv", sep=";")
df = pd.read_csv("SentToLabel_15-5_Revisited.csv", sep=";")
print(len(df))

# df = df[:1000] # should not be active
print(len(df))

data = df["data"].to_list()
labels = df["label"].to_list()

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

print("Splitting data")
## CHANGE THIS ##
# X_train, X_val, y_train, y_val = train_test_split(data, labels, test_size=0.01, random_state=1212)
X_train, X_val, y_train, y_val = train_test_split(data, labels, test_size=0.1, random_state=1212)

data = 0
labels = 0

start_time = time.time()
print("Tokenizing val:")
X_val_tokenized = tokenizer(X_val, padding=True, truncation=True)
print("Time taken for validation: ", time.time() - start_time)
print("Expected total time ", ((time.time() - start_time) * 10) // 60, "min", ((time.time() - start_time) * 10) % 60, "sek")
X_train_tokenized = tokenizer(X_train, padding=True, truncation=True)
print("Done with tokenization")

## CHANGE THIS ##
batch_size = 32
# batch_size = 4
epochs = 2

train_dataset = CustomDataset(X_train_tokenized, y_train, batch_size=batch_size)
val_dataset = CustomDataset(X_val_tokenized, y_val, batch_size=batch_size)
## CHANGE THESE ##
# os.chdir("/Users/lucasvilsen/Desktop/GrammatikTAK/FineTuneModels/CommaModels")
# device = "mps"
device = "cuda:0"
torch.device(device)
model = BertForSequenceClassification.from_pretrained('Geotrend/distilbert-base-da-cased', num_labels=3)
model.to(device)

args = TrainingArguments(
    evaluation_strategy="steps",
    save_strategy="steps",
    learning_rate=2e-5,
    per_device_train_batch_size=batch_size,
    per_device_eval_batch_size=batch_size,
    num_train_epochs=epochs,
    weight_decay=0,
    load_best_model_at_end=True,
    metric_for_best_model="accuracy",
    eval_steps=5000,  
    output_dir="output",
    logging_steps=1000,
    logging_dir = "log", 
    save_steps = 5000,
    save_total_limit = 3
)

def compute_metrics(eval_preds):
    metric = load_metric("accuracy")
    logits, labels = eval_preds
    predictions = np.argmax(logits, axis=-1)
    return metric.compute(predictions=predictions, references=labels)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics
)

trainer.train()

torch.save(model, './commaDistilBERT1')