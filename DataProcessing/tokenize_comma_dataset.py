import os
import pandas as pd
from tqdm import tqdm

from transformers import BertTokenizer, BertModel, BertForSequenceClassification, TrainingArguments, Trainer
from sklearn.model_selection import train_test_split

import pickle

current_dir = os.getcwd()
os.chdir("/Users/lucasvilsen/Desktop/GrammatikTAK/Datasets/")

df = pd.read_csv("EuroparlWithPadding15-5.csv", sep=";", encoding="UTF-8")

X = list(df["comment_text"])
y = list(df["label"])
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.1, random_state=1212)
tokenizer = BertTokenizer.from_pretrained('Maltehb/danish-bert-botxo')

X_train_tokenized = []
for text in tqdm(X_train, desc="Tokenizing X_train"):
    tokens = tokenizer(
        text
    )
    X_train_tokenized.append(tokens)

with open('train_tokenized.pkl', 'wb') as file:
    pickle.dump(X_train_tokenized, file)

with open('y_train.pkl', 'wb') as file:
    pickle.dump(y_train, file)

y_train_df = pd.DataFrame(y_train)
y_train_df.to_csv('y_train.csv', index=False)
print("train done")

X_val_tokenized = []
for text in tqdm(X_val, desc="Tokenizing X_val"):
    tokens = tokenizer(
        text
    )
    X_val_tokenized.append(tokens)

with open('val_tokenized.pkl', 'wb') as file:
    pickle.dump(X_val_tokenized, file)

with open('y_val.pkl', 'wb') as file:
    pickle.dump(y_val, file)
print("val done")

