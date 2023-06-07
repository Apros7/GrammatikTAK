import os
import pandas as pd
from tqdm import tqdm
import pickle

###################################################################
## MAKE SURE TO HAVE THE UPDATED EUROPARL SENT TO POS IN DATASET ##
###################################################################

os.chdir("/Users/lucasvilsen/Desktop/GrammatikTAK/Datasets/")
filename = "europarl-v7.da-en.da"
with open(filename, "r", encoding="UTF-8") as file:
    lines = file.readlines()
with open("nutids_r_bøjninger.pickle", "rb") as f:
    nutids_r_bøjninger = pickle.load(f)
with open("nutids_r_stem.pickle", "rb") as f:
    nutids_r_stem = pickle.load(f)

# If changed all of the dataset also needs to be changed

padding_left = 15
padding_right = 5

testset = []
labels = []
testset_words = []

df = pd.read_csv("../Datasets/EuroparlSentToPos.csv", encoding="UTF-8", sep=";")
df_filtered = df.dropna(subset=["pos"])
sentences = list(df_filtered["sent"])
all_pos = list(df_filtered["pos"])
print("len(df_filtered):", len(df_filtered))

def get_pos_tags(index):
    return all_pos[index].split()

for i in tqdm(range(len(sentences))):
    line = sentences[i]
    if len(str(line)) < 1 or str(line) == "nan":
        continue
    line = line.strip("\n")
    true_words = line.split()
    pos = get_pos_tags(i)
    words = ["<PAD>"]*padding_left + pos + ["<PAD>"]*padding_right
    words_with_padding = ["<PAD>"]*padding_left + true_words + ["<PAD>"]*padding_right
    for i, word in enumerate(true_words):
        try: stemmed = nutids_r_stem[word]
        except: continue
        if word[-1] == "s":
            continue
        if nutids_r_bøjninger[stemmed][0] == word:
            labels.append(1)
        else:
            labels.append(0)
        testset.append(" ".join(words[i:i+padding_left+padding_right+1]))
        current_words = words_with_padding[i:i+padding_left+padding_right+1]
        current_words[padding_left] = "[MASK]"
        if words[i+padding_left] == "VERB":
            testset_words.append(" ".join(current_words))

df = pd.DataFrame(zip(testset, labels), columns=["comment_text", "label"])
all_pos = list(set([x for test in testset for x in test.split()]))

comment_text = df["comment_text"].values
mistakes = [l for l in comment_text if not l.isupper()]
middle = [l.split()[padding_left] for l in comment_text]

print(df["label"].value_counts())

from collections import Counter

counter = Counter(middle)
for key, value in counter.items():
    print(key, ": ", value)

df.to_csv("../Datasets/EuroparlNutidsr_trainset.csv", encoding="UTF-8", index=False, sep=";")

df2 = pd.DataFrame(zip(testset_words, labels), columns=["comment_text", "label"])
df2.to_csv("../Datasets/EuroparlNutidsrWords_trainset.csv", encoding="UTF-8", index=False, sep=";")

verb_text_and_labels = [(c, l) for c, l in zip(comment_text, labels) if c.split()[padding_left] == "VERB"]
verb_text = [c for c, l in verb_text_and_labels]
verb_labels = [l for c, l in verb_text_and_labels]

df = pd.DataFrame(zip(verb_text, verb_labels), columns=["comment_text", "label"])
df.to_csv("../Datasets/EuroparlNutidsr_trainset_verbs.csv", encoding="UTF-8", index=False, sep=";")
print(df)

counts = {i: 0 for i in range(20)}
for sentence in verb_text:
    num_pads = sentence.count("<PAD>")
    counts[num_pads] += 1

from tabulate import tabulate

table = [["Number of <PAD> occurrences", "Number of sentences"]]
for i in range(20):
    table.append([i, counts[i]])

print(tabulate(table, headers="firstrow", tablefmt="github"))