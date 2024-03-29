from transformers import AutoTokenizer, AutoModel
import torch
from torch.utils.data import Dataset, DataLoader
from datasets import load_metric
import pandas as pd
from sklearn.model_selection import train_test_split
import time
import numpy as np
from transformers import TrainingArguments, Trainer, AutoModelForSequenceClassification, BertForSequenceClassification, DistilBertForSequenceClassification
import os

# scp -P 8128 Desktop/europarl-v7.da-en.da root@sshd.jarvislabs.ai:/root
# pip3 install accelerate -U
# pip3 install datasets scikit-learn transformers pandas
# Desktop/GrammatikTAK/FineTuneModels/CommaModels/DistilBERTSentToLabel.py

tokenizer = AutoTokenizer.from_pretrained("Geotrend/distilbert-base-da-cased")

## CHANGE THIS ##
# os.chdir("/Users/lucasvilsen/Desktop/GrammatikTAK/Datasets")
# df = pd.read_csv("SentToLabel_15-5_Revisited_small.csv", sep=";")

df = pd.read_csv("SentToLabel_15-5_Revisited.csv", sep=";")
print(len(df))

# df = df[:28000000] # should not be active
# df = df[:400000]
print(len(df))

data = df["data"].to_list()
labels = df["label"].to_list()

df = 0

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
test_size = 0.05
X_train, X_val, y_train, y_val = train_test_split(data, labels, test_size=test_size, random_state=1212)
print("Len x train: ", len(X_train))

data = 0
labels = 0

start_time = time.time()
print("Tokenizing val:")

# X_val_tokenized2 = {"attention_mask": [], "input_ids": []}
# batch_size = 64

# for i in tqdm(range(0, len(X_val), batch_size), desc="Tokenizing"):
#     tokenized_text = tokenizer(X_val[i:i+batch_size], padding=True, truncation=True)
#     for k in tokenized_text:
#         X_val_tokenized2[k].extend(tokenized_text[k])

X_val_tokenized = tokenizer.batch_encode_plus(X_val, padding=True, truncation=True)

# for k, v in X_val_tokenized2.items():
#     print(v == X_val_tokenized[k])
#     # print(v)
#     # print(X_val_tokenized[k])

# print(X_val_tokenized.keys())

X_val = 0
print("Time taken for validation: ", time.time() - start_time)
print("Expected total time ", ((time.time() - start_time) * 1/test_size) // 60, "min", ((time.time() - start_time) * 1/test_size) % 60, "sek")

start_time = time.time()
X_train_tokenized = tokenizer.batch_encode_plus(X_train, padding=True, truncation=True)
print("Len x train tokenized: ", len(X_train_tokenized))
print(time.time() - start_time)

# X_train_tokenized2 = {"attention_mask": [], "input_ids": []}
# batch_size = 64

# for i in tqdm(range(0, len(X_train), batch_size), desc="Tokenizing"):
#     tokenized_text = tokenizer(X_train[i:i+batch_size], padding=True, truncation=True)
#     for k in tokenized_text:
#         X_train_tokenized2[k].extend(tokenized_text[k])

# for k, v in X_train_tokenized2.items():
#     print(v == X_train_tokenized[k])

print("Done with tokenization")
X_train = 0

## CHANGE THIS ##
batch_size = 32
# batch_size = 4
epochs = 2

train_dataset = CustomDataset(X_train_tokenized, y_train, batch_size=batch_size)
print("Len x train dataset: ", len(train_dataset))
# print("Supposed train steps: ", len(train_dataset) * epochs // batch_size)
# print("Supposed train steps: ", (factor * len(train_dataset) * epochs // batch_size) / 7)
val_dataset = CustomDataset(X_val_tokenized, y_val, batch_size=batch_size)
## CHANGE THESE ##
# os.chdir("/Users/lucasvilsen/Desktop/GrammatikTAK/FineTuneModels/CommaModels")
# device = "mps"
device = "cuda:0"
torch.device(device)
# model = BertForSequenceClassification.from_pretrained('Geotrend/distilbert-base-da-cased', num_labels=3) # about 6:10
model = DistilBertForSequenceClassification.from_pretrained('Geotrend/distilbert-base-da-cased', num_labels=3) # about 3:30
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
    eval_steps=100000,  
    output_dir="output",
    logging_steps=25000,
    logging_dir = "log", 
    save_steps = 100000,
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

# os.chdir("/Users/lucasvilsen/Desktop/GrammatikTAK/FineTuneModels/CommaModels")

torch.save(model, './commaDistilBERT1.pt')