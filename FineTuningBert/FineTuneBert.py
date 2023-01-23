import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer, BertModel, BertForSequenceClassification, TrainingArguments, Trainer
from sklearn.model_selection import train_test_split
from datasets import load_metric
import numpy as np

# Set the device
#device = 'cuda' if torch.cuda.is_available() else 'cpu'
device = "mps"
torch.device(device)

# Load the dataset
df = pd.read_csv("Datasets/DanavisDF.csv")
df = df[:100000]
#max_len = max([len(sent) for sent in df["comment_text"]])
X = list(df["comment_text"])
y = list(df["label"])

# Split the dataset into train and test sets
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=1212)

# Tokenize the input data
tokenizer = BertTokenizer.from_pretrained('Maltehb/danish-bert-botxo')
X_train_tokenized = tokenizer(X_train, padding=True, truncation=True, max_length=60)
X_val_tokenized = tokenizer(X_val, padding=True, truncation=True, max_length=60)

# Define a dataset class
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

# Set the batch size
batch_size = 32
epochs = 3

# Create the train and test datasets
train_dataset = CustomDataset(X_train_tokenized, y_train, batch_size=batch_size)
val_dataset = CustomDataset(X_val_tokenized, y_val, batch_size=batch_size)

# Create the model
model = BertForSequenceClassification.from_pretrained('Maltehb/danish-bert-botxo', num_labels=3)
#model = torch.load("modelCombined2")
model.to(device)

# Define the training arguments
args = TrainingArguments(
    output_dir="output",
    evaluation_strategy="epoch",
    save_strategy="epoch",
    learning_rate=1e-4,
    per_device_train_batch_size=batch_size,
    per_device_eval_batch_size=batch_size,
    num_train_epochs=epochs,
    weight_decay=0.001,
    load_best_model_at_end=True
    #metric_for_best_model="accuracy",
)

# Define a metric for evaluation
def compute_metrics(eval_preds):
    metric = load_metric("accuracy")
    logits, labels = eval_preds
    predictions = np.argmax(logits, axis=-1)
    return metric.compute(predictions=predictions, references=labels)

# Create the trainer
trainer = Trainer(
    model=model,
    args=args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics
)

# Start training
trainer.train()

# Evaluate the model on the test set
trainer.evaluate()

# Save the trained model
torch.save(model, './modelCombined4')

