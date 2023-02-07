from transformers import BertTokenizer, BertForSequenceClassification
from transformers import EarlyStoppingCallback
from transformers import Trainer, TrainingArguments
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, recall_score, precision_score
import pandas as pd
import numpy as np
import torch

tokenizer = BertTokenizer.from_pretrained("Maltehb/danish-bert-botxo")
#model = BertForSequenceClassification.from_pretrained("Maltehb/danish-bert-botxo", num_labels = 2)

# Load data
#data = pd.read_csv("Datasets/TextLineDataDanavisDFcomma.csv")
data = pd.read_csv("Datasets/DanavisDF.csv")
data = data.rename(columns={"output": "label", "comment_text": "text"})

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

# Create testing dataset
test_data = data[200000:205000]
X_test = list(test_data["text"])
X_test_tokenized = tokenizer(X_test, padding=True, truncation=True, max_length=512)
test_dataset = Dataset(X_test_tokenized)

models = ["modelCombined", "modelCombined2", "modelCombined3", "modelCombined4"]
scores = []

for i in range(4):
    # Load model
    model = torch.load(models[i])
    model.eval()
    test_trainer = Trainer(model)
    raw_pred, _, _ = test_trainer.predict(test_dataset)
    y_pred = np.argmax(raw_pred, axis=1)

    # Compare lists
    correct_y = np.array(test_data["label"].values)
    alike0 = []
    alike0_len = 0
    alike1 = []
    alike1_len = 0

    for correct, pred in zip(correct_y, y_pred):
        if correct == pred:
            if correct == 0:
                alike0.append(pred)
            else:
                alike1.append(pred)
        if correct == 0:
            alike0_len += 1
        else:
            alike1_len += 1

    print(f"procent of no comma sentences: {100*alike0_len/len(correct_y)}")
    print(f"correct placement for no comma = {100*len(alike0)/alike0_len}")
    print(f"correct placement for comma= {100*len(alike1)/alike1_len}")


