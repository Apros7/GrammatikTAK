import pandas as pd
import numpy as np

train_verbs = pd.read_csv("Datasets/EuroparlNutidsr_trainset_verbs.csv", sep=";")
pos_lines = [line.split() for line in train_verbs["comment_text"]]
pos_words = list(set([word for line in pos_lines for word in line]))

pos_words_to_numbers = {word: i for i, word in enumerate(pos_words)}
numbers_to_pos_words = {i: word for i, word in enumerate(pos_words)}

pos_numbers = []

for line in pos_lines:
    indexes = []
    for word in line:
        index = pos_words_to_numbers[word]
        indexes.append(str(index))
    pos_numbers.append(" ".join(indexes))


print(pos_words_to_numbers)
print(pos_numbers[:1])
train_verbs["pos_numbers"] = pos_numbers

train_verbs.to_csv("Datasets/EuroparlNutidsr_trainset_posNumbers.csv", sep=";", index=False)