import torch.nn as nn
import torch
import os
import pandas as pd
from sklearn.model_selection import train_test_split
import random
from tqdm import tqdm
import numpy as np
import pickle

os.chdir("/Users/lucasvilsen/Desktop/GrammatikTAK/Datasets/")
filename = "EuroparlNutidsr_trainset_verbs.csv"
print("Loading df...")
df = pd.read_csv(filename, encoding="UTF-8", sep=";")
pos = list(df["comment_text"].values)
labels = list(df["label"].values)

X_train, X_test, y_train, y_test = train_test_split(pos, labels, test_size=0.1, random_state=42)

unique_pos = ['NOUN','PUNCT','VERB','PRON','NUM','ADP','X','<PAD>','CCONJ','PROPN','AUX','SCONJ','INTJ','ADV','ADJ','PART','SYM','DET']


class NutidsrTokenizer():
    def __init__(self) -> None:
        print("Initializing tokenizer...")
        self.tokenize_table = {x: i for i, x in enumerate(unique_pos)}
        print("Tokenizer initialized.")

    def __call__(self, pos_list):
        for pos_string in tqdm(pos_list):
            splitted_pos = pos_string.split()
            numbers = [self.tokenize_table[x] for x in splitted_pos]
            yield [y for x in numbers for y in self._one_hot_encode(x)]
    
    def _one_hot_encode(self, number):
        return [1 if i == number else 0 for i in range(18)]

class NutidsrModel(nn.Module):
    def __init__(self) -> None:
        super(NutidsrModel, self).__init__()
        number_of_unique_pos = 18
        number_of_pos_including_padding = 21
        self.l1 = nn.Linear(number_of_pos_including_padding*number_of_unique_pos, 256)
        self.l2 = nn.Linear(256, 256)
        self.l3 = nn.Linear(256, 64)
        self.l4 = nn.Linear(64, 1)
        self.activation = nn.LeakyReLU(0.2)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.l1(x)
        x = self.activation(x)
        x = self.l2(x)
        x = self.activation(x)
        x = self.l3(x)
        x = self.activation(x)
        x = self.l4(x)
        x = self.sigmoid(x)
        return x

tokenizer = NutidsrTokenizer()
print("Tokenizing train...")
x_train_tokenized = list(tokenizer(X_train))
print("Tokenizing test...")
x_test_tokenized = list(tokenizer(X_test))
print("Done Tokenizing.")

EPOCHS, BATCH_SIZE = 10, 128

model = NutidsrModel()
optimizer = torch.optim.Adam(model.parameters(),lr=0.0002, betas=(0.5, 0.999))
device = "cpu"
loss_fn = nn.MSELoss()
torch.device(device)
model.to(device)


n_steps = len(x_train_tokenized) // BATCH_SIZE
eval_steps = len(x_test_tokenized) // BATCH_SIZE

print("Training model...")
print("INFO: Epochs: ", EPOCHS, ". Batch size: ", BATCH_SIZE, ". Steps pr. epoch: ", n_steps, ". Eval steps: ", eval_steps)

def get_batch(x, y):
    indexes = random.sample(range(len(x)), BATCH_SIZE)
    x_batch = [x[i] for i in indexes]
    y_batch = [y[i] for i in indexes]
    return x_batch, y_batch

def train_model(xb, yb):
    yb = torch.tensor(yb, dtype=torch.float32)
    optimizer.zero_grad()
    output = model.forward(xb)
    loss = loss_fn(output, yb)
    loss.backward()
    optimizer.step()
    return loss

def test_model():
    accuracies = []
    for i in tqdm(range(eval_steps)):
        xb, yb = get_batch(x_test_tokenized, y_test)
        xb = torch.tensor(xb)
        output = list(model.forward(xb))
        accuracy = sum([1 if to_binary(o.numpy()) == y else 0 for (o,y) in zip(output, yb)])/len(output)
        accuracies.append(accuracy)
        del xb, yb, output, accuracy
    print("Eval accuracy: ", round(sum(accuracies)/len(accuracies)*100, 2), "%")

def to_binary(o):
    return 1 if o > 0.5 else 0

def save_model(epoch):
    os.makedirs("simpleNNmodelsPT", exist_ok=True)
    torch.save(model.state_dict(), f"simpleNNmodelsPT/model_{epoch}.pt")

print("Accuracy before training: ")
test_model()
save_model(-1)


for epoch in range(EPOCHS):
    model.train()
    for i in tqdm(range(n_steps)):
        xb, yb = get_batch(x_train_tokenized, y_train)
        xb = torch.tensor(xb)
        loss = train_model(xb, yb)
        if i % 3000 == 0:
            print(f"Loss at step {i}: {-loss}")
    
    print(f"Done with Epoch {epoch}")
    print("Evaluating...")
    model.eval()

    test_model()
    save_model(epoch)

        

