from tinygrad.tensor import Tensor
from tinygrad.nn import optim
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
print("Done loading df...")
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

class NutidsrModel():

    def __init__(self) -> None:
        number_of_unique_pos = 18
        number_of_pos_including_padding = 21
        self.l1 = Tensor.scaled_uniform(number_of_pos_including_padding*number_of_unique_pos, 256)
        self.l2 = Tensor.scaled_uniform(256, 256)
        self.l3 = Tensor.scaled_uniform(256, 64)
        self.l4 = Tensor.scaled_uniform(64, 1)

    def forward(self, x):
        x = x.dot(self.l1).leakyrelu(0.2)
        x = x.dot(self.l2).leakyrelu(0.2)
        x = x.dot(self.l3).leakyrelu(0.2)
        x = x.dot(self.l4).sigmoid()
        return x

tokenizer = NutidsrTokenizer()
print("Tokenizing train...")
x_train_tokenized = list(tokenizer(X_train))
print("Tokenizing test...")
x_test_tokenized = list(tokenizer(X_test))
print("Done Tokenizing.")

EPOCHS, BATCH_SIZE = 10, 64

model = NutidsrModel()
optimizer = optim.Adam(optim.get_parameters(model),lr=0.0002, b1=0.5)

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
    yb = Tensor([yb])
    optimizer.zero_grad()
    output = model.forward(xb)
    loss = (output * yb).mean()
    loss.backward()
    optimizer.step()
    return loss.cpu().numpy()

def test_model():
    accuracies = []
    for i in tqdm(range(eval_steps)):
        xb, yb = get_batch(x_test_tokenized, y_test)
        xb = Tensor(xb, requires_grad=False)
        output = list(model.forward(xb))
        ## Needs to convert float to either 0 or 1
        accuracy = sum([1 if to_binary(o.numpy()) == y else 0 for (o,y) in zip(output, yb)])/len(output)
        accuracies.append(accuracy)
    print("Eval accuracy: ", round(sum(accuracies)/len(accuracies)*100, 2), "%")

def to_binary(o):
    return 1 if o > 0.5 else 0

def save_model(epoch):
    os.makedirs("simpleNNmodels", exist_ok=True)
    params = model.get_parameters()
    with open("simpleNNmodels/nn1_epoch:"+str(epoch)+".pkl", "wb") as f:
        pickle.dump(params, f)

print("Accuracy before training: ")
test_model()
save_model(-1)


for epoch in range(EPOCHS):
    for i in tqdm(range(n_steps)):
        xb, yb = get_batch(x_train_tokenized, y_train)
        xb = Tensor(xb, requires_grad=True)
        loss = train_model(xb, yb)
        if i % 3000 == 0:
            print(f"Loss at step {i}: {-loss}")
    
    print(f"Done with Epoch {epoch}")
    print("Evaluating...")

    test_model()
    save_model(epoch)

        

