
import os
import numpy as np
import pandas as pd
from tqdm import tqdm
from misspeller_class import Misspeller

misspeller = Misspeller()

os.chdir("/Users/lucasvilsen/Desktop/GrammatikTAK/Datasets/")

with open("europarl-v7.da-en.da", "r", encoding="UTF-8") as file:
    pre_cleaned_lines = file.readlines()
lines = [line.replace("\n", "") for line in pre_cleaned_lines]
lines = lines[:1]

with open("ordlisteFuldform2021OneRow.csv", "r") as file:
    non_cleaned_dictionary = file.readlines()

dictionary = [line.replace("\n", "").lower() for line in non_cleaned_dictionary]

dictionary = dictionary
word_lst = []
permutations = []
permutations_len = []

for dict_word in tqdm(dictionary):
    word_permutations = misspeller.get_permutations(dict_word)
    word_lst.append(dict_word)
    permutations.append("|".join(word_permutations))
    permutations_len.append(len(word_permutations))

print("Average len: ", np.mean(permutations_len))
df = pd.DataFrame({"word": word_lst, "permutations": permutations})
df.to_csv("misspellings.csv", index=False)

words = df["word"].tolist()
non_listed_permutations = df["permutations"].tolist()
permutations = [permutation.split("|") for permutation in non_listed_permutations]

from tqdm import tqdm

misspelling_dict = {}

for i in tqdm(range(len(words))):
    word = words[i]
    permutation_lst = permutations[i]
    for permutation in permutation_lst:
        if permutation != word:
            if permutation not in misspelling_dict:
                misspelling_dict[permutation] = [word]
            else:
                misspelling_dict[permutation].append(word)

for k, v in tqdm(misspelling_dict.items()):
    misspelling_dict[k] = list(set(v))

import pickle

with open("misspellings_dict.pickle", "wb") as file:
    pickle.dump(misspelling_dict, file)

dictionary = [x.lower() for x in dictionary]

with open("dictionary.pickle", "wb") as file:
    pickle.dump(dictionary, file)
