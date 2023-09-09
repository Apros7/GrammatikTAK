
## This file serves as the basic foundation for choosing to train a 
# BERT on complete sentences instead of one word at a time.

import os
import matplotlib.pyplot as plt

os.chdir("/Users/lucasvilsen/Desktop/GrammatikTAK/Datasets/")

filename = "europarl-v7.da-en.da"
with open(filename, "r", encoding="UTF-8") as file:
    lines = file.readlines()

sentence_lens = sorted([len(line.split()) for line in lines])
# print(min(sentence_lens), max(sentence_lens))

plt.hist(sentence_lens, bins=100)
# plt.show()

def procent_under(value):
    index = sentence_lens.index(value)
    under_chosen_len = len(sentence_lens[:index])
    print(f"Procent under {value}: ", under_chosen_len/len(sentence_lens) * 100, "%")
    print(f"Number of sentences over {value}: {len(sentence_lens) - under_chosen_len}")

for value in [30, 40, 50, 70, 90, 110, 130, 150, 200]: 
    procent_under(value)