import os
from tqdm import tqdm
import pandas as pd

current_dir = os.getcwd()
print(current_dir)
os.chdir("/Users/lucasvilsen/Desktop/GrammatikTAK/DataCreationDatasets/")
all_files = os.listdir()
print(len(all_files))
lines = [open(file).readlines() for file in all_files]
big_words = [line.strip("\"") for lst in lines for line in lst]
print(len(big_words))

char = ["*", "@", ";", ":", "!", "\"", "?", "«", "»"]
symbol = [".", ","]
big_lst = []
output1_lst = []

# Changing to six words scope
scope = 6
middle = int(scope/2)
padding = int(scope/2-1)

old_big_words = big_words

# add padding
padded_big_words = []
for i in tqdm(range(len(old_big_words))):
    word = old_big_words[i]
    if word[-1] == ".":
        for _ in range(padding):
            big_words.append("<PAD>")
        padded_big_words.append(word)
        for _ in range(padding):
            padded_big_words.append("<PAD>")
    else:
        padded_big_words.append(word)

print(len(padded_big_words))
big_words = []
for lst in padded_big_words:
    big_words += lst.split()

print(len(big_words))

for x in tqdm(range(len(big_words)-4)):
    four_words = big_words[x:x+scope]
    if any([x == y for y in char for x in four_words]):
        continue
    # could be full stop. Here is none (change output1 to achieve multiclass dataset)
    if four_words[middle] == symbol[0]:
        output1 = 0
        four_words = big_words[x:x+scope+1]
        four_words.remove(symbol[0])
    elif any([x == symbol[0] for x in four_words]):
        continue
    elif four_words[middle] == symbol[1]:
        output1 = 1
        four_words = big_words[x:x+scope+1]
        four_words.remove(symbol[1])
    elif any([x == symbol[1] for x in four_words]):
            continue
    else:
        output1 = 0
    if (sum([1 if x == "<PAD>" else 0 for x in four_words]) > padding):
        continue
    big_lst.append((" ".join(four_words)).lower())
    output1_lst.append(output1)

os.chdir(current_dir)
df = pd.DataFrame()
df["comment_text"] = big_lst
df["label"] = output1_lst
print(len(df))

header = ["comment_text", "label"]
df.to_csv("GrammatiktakDatasets/checkedDatasets/CommaDevelopmentset.csv", encoding="UTF-8", index=False)