
from transformers import AutoTokenizer, Trainer, BertTokenizer
import torch.nn as nn
import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
import time
import torch
import random
from tqdm import tqdm
from sklearn.metrics import accuracy_score

os.chdir("/Users/lucasvilsen/Desktop/GrammatikTAK/Datasets")

tokenizer = AutoTokenizer.from_pretrained("Geotrend/distilbert-base-da-cased")

print("Loading Data")

df_distil = pd.read_csv("SentToLabel_15-5_Revisited.csv", sep=";")
print(len(df_distil))

# df_distil = pd.read_csv("SentToLabel_15-5_Revisited.csv", sep=";")
# print(len(df_distil))

data = df_distil["data"].to_list()
labels = df_distil["label"].to_list()

data = data[:3000000]
labels = labels[:3000000]

labels = torch.stack([torch.eye(3)[number] for number in labels])

del df_distil

print("Tokenizing")
tokenized_data = tokenizer(data, padding=True, truncation=True, max_length=75)
input_ids = tokenized_data["input_ids"]

del tokenized_data

print("Splitting data")
X_train, X_test, y_train, y_test = train_test_split(input_ids, labels, test_size=0.1, random_state=42)

del input_ids, labels

print("Initializing model")

class CommaModel(nn.Module):
    def __init__(self) -> None:
        super(CommaModel, self).__init__()
        self.l1 = nn.Linear(75, 8192)
        self.l2 = nn.Linear(8192, 8192)
        self.l4 = nn.Linear(8192, 64)
        self.l5 = nn.Linear(64, 3)
        self.activation = nn.Tanh()
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.l1(x)
        x = self.activation(x)
        x = self.l2(x)
        x = self.activation(x)
        x = self.l4(x)
        x = self.activation(x)
        x = self.l5(x)
        x = self.sigmoid(x)
        return x

model = CommaModel()
print("Parameters: ", sum(p.numel() for p in model.parameters()))

EPOCHS, BATCH_SIZE = 100, 128

optimizer = torch.optim.Adam(model.parameters(),lr=0.00001, betas=(0.5, 0.999))
device = "cpu"
loss_fn = nn.MSELoss()
torch.device(device)
model.to(device)


n_steps = len(X_train) // BATCH_SIZE
eval_steps = len(X_test) // BATCH_SIZE

print("Training model...")
print("INFO: Epochs: ", EPOCHS, ". Batch size: ", BATCH_SIZE, ". Steps pr. epoch: ", n_steps, ". Eval steps: ", eval_steps)

def get_batch(x, y):
    indexes = random.sample(range(len(x)), BATCH_SIZE)
    x_batch = [x[i] for i in indexes]
    y_batch = [y[i] for i in indexes]
    return x_batch, y_batch

def train_model(xb, yb):
    model.train()
    # yb = torch.tensor(yb, dtype=torch.float32)
    optimizer.zero_grad()
    xb = torch.tensor(xb, dtype=torch.float32)
    output = model.forward(xb)
    loss = loss_fn(output, yb)
    loss.backward()
    optimizer.step()
    return loss

def test_model():
    model.eval()
    accuracies = []
    for _ in tqdm(range(eval_steps)):
        xb, yb = get_batch(X_test, y_test)
        xb = torch.tensor(xb, dtype=torch.float32)
        output = model.forward(xb)
        true_predictions = np.argmax(output.detach().numpy(), axis=1)
        yb = torch.argmax(torch.stack(yb), dim=1)
        accuracies.append(accuracy_score(yb, true_predictions))
        del xb, yb, output, true_predictions
    print("Eval accuracy: ", round(sum(accuracies)/len(accuracies)*100, 2), "%")

def save_model(epoch):
    os.makedirs("simpleNNmodelsPT", exist_ok=True)
    torch.save(model.state_dict(), f"simpleNNmodelsPT/model_{epoch}.pt")

print("Accuracy before training: ")
accuracy_begin = test_model()
save_model(-1)

eval_accuracy = []
losses = []

for epoch in range(EPOCHS):
    for i in tqdm(range(n_steps)):
        xb, yb = get_batch(X_train, y_train)
        yb = torch.stack(yb)
        xb = torch.tensor(xb)
        loss = train_model(xb, yb)
        if i % 5000 == 0 and i != 0:
            print(f"Loss at step {i}: {loss}")
            test_model()
    
    print(f"Done with Epoch {epoch}")
    print("Evaluating...")

    test_model()
    save_model(epoch)