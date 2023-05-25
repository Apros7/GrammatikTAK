import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer, BertModel, BertForSequenceClassification, TrainingArguments, Trainer
from sklearn.model_selection import train_test_split
from datasets import load_metric
import numpy as np
import os

df = pd.read_csv("EuroparlWithPadding15-5.csv", sep=";")
df = df.dropna(subset=["label"])
df["label"] = df["label"].astype(int)
df = df.reset_index()[["comment_text", "label"]]
df = df[:10000]

device = "cuda"
torch.device(device)

X = list(df["comment_text"])
y = list(df["label"])
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.1, random_state=1212)
tokenizer = BertTokenizer.from_pretrained('Maltehb/danish-bert-botxo')
X_train_tokenized = tokenizer(X_train, padding=True, truncation=True)
X_val_tokenized = tokenizer(X_val, padding=True, truncation=True)

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

batch_size = 32
epochs = 2

# Create the train and test datasets
train_dataset = CustomDataset(X_train_tokenized, y_train, batch_size=batch_size)
val_dataset = CustomDataset(X_val_tokenized, y_val, batch_size=batch_size)

# Create the model
model = BertForSequenceClassification.from_pretrained('Maltehb/danish-bert-botxo', num_labels=2)
#model = torch.load("modelCombined2")
model.to(device)

args = TrainingArguments(
    output_dir="output",
    evaluation_strategy="epoch",
    save_strategy="epoch",
    learning_rate=1e-5,
    per_device_train_batch_size=batch_size,
    per_device_eval_batch_size=batch_size,
    num_train_epochs=epochs,
    weight_decay=0,
    load_best_model_at_end=True,
    metric_for_best_model="accuracy"
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

torch.save(model, './commaModel10')