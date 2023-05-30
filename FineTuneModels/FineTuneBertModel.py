from transformers import BertTokenizer, BertForSequenceClassification
from transformers import EarlyStoppingCallback
from transformers import Trainer, TrainingArguments
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, recall_score, precision_score
import pandas as pd
import numpy as np
import torch

tokenizer = BertTokenizer.from_pretrained("Maltehb/danish-bert-botxo")
model = BertForSequenceClassification.from_pretrained("Maltehb/danish-bert-botxo", num_labels = 3)
#model = torch.load("./modelPunctuation")
#model.train()

# Load / Clean data
data = pd.read_csv("Datasets/DanavisDF.csv")
data = data.rename(columns={"output": "label", "four_words": "text"})
data_sample = data[:50000]
# Trænet til 50.000 epoch 2

# Preprocessing
X = list(data_sample["text"])
y = list(data_sample["label"])
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=1212)
X_train_tokenized = tokenizer(X_train, padding=True, truncation=True, max_length=512)
X_val_tokenized = tokenizer(X_val, padding=True, truncation=True, max_length=512)

# Create datasets
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

train_dataset = Dataset(X_train_tokenized, y_train)
val_dataset = Dataset(X_val_tokenized, y_val)

def compute_metrics(p):
    pred, labels = p
    pred = np.argmax(pred, axis=1)

    accuracy = accuracy_score(y_true=labels, y_pred=pred)
    recall = recall_score(y_true=labels, y_pred=pred)
    precision = precision_score(y_true=labels, y_pred=pred)
    f1 = f1_score(y_true=labels, y_pred=pred)

    return {"accuracy": accuracy, "precision": precision, "recall": recall, "f1": f1}

batch_size = 32

args = TrainingArguments(
    output_dir="output",
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=batch_size,
    per_device_eval_batch_size=batch_size,
    num_train_epochs=2,
    weight_decay = 0.01
)
trainer = Trainer(
    model=model,
    args=args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics,
    tokenizer=tokenizer,
)

# Train pre-trained model
trainer.train()
torch.save(model, './model')