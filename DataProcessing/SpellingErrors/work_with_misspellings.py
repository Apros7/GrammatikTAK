import pandas as pd
from tqdm import tqdm
import os
import pickle
import random
import time

os.chdir("/Users/lucasvilsen/Desktop/GrammatiktakDatasets/Danish")

df = pd.read_csv("spelling_errors.csv", sep="|")

start = time.time()

os.chdir("/Users/lucasvilsen/Desktop/GrammatikTAK/Datasets/")

with open("misspellings_dict.pickle", "rb") as file:
    misspelling_dict = pickle.load(file)

print(time.time() - start)

start = time.time()

df_misspellings = pd.read_csv("misspellings_dict.csv")
words = df_misspellings["word"].tolist()
misspellings = df_misspellings["misspellings"].tolist()

misspelling_dict = {word: misspelling for word, misspelling in zip(words, misspellings)}

print(time.time() - start)


larger_than_two = {k:v for (k, v) in misspelling_dict.items() if len(v) > 1}
rnumbers = [random.randint(0, len(larger_than_two)) for _ in range(10)]
larger_than_two_items = list(larger_than_two.items())
print(*[larger_than_two_items[i] for i in rnumbers], sep="\n")

print(len(misspelling_dict.values()), len([value for value in misspelling_dict.values() if len(value) > 1]))
print(len([value for value in misspelling_dict.values() if len(value) > 2]))
print(len([value for value in misspelling_dict.values() if len(value) > 3]))
print(len([value for value in misspelling_dict.values() if len(value) > 4]))

wrongs = df["wrong"].to_list()
rights = df["right"].to_list()

correct = 0
total = 0
mistakes = []

for wrong, right in zip(wrongs, rights):
    if wrong in misspelling_dict.keys():
        total += 1
        if right in misspelling_dict[wrong]:
            correct += 1
        else:
            mistakes.append((wrong, misspelling_dict[wrong], right))

print("SCORE: ", correct / total, correct, total)
print("MISTAKES: ", len(mistakes))
print(*mistakes, sep="\n")

# With keyboard mistakes: 35.854.38
# Without keyboard mistakes: 22.674.797 -> 129367 with two or more possible corrections