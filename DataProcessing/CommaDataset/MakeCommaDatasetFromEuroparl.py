import os
import pandas as pd
from tqdm import tqdm

current_dir = os.getcwd()
os.chdir("/Users/lucasvilsen/Desktop/GrammatikTAK/Datasets/")
big_lst = []
output1_lst = []
char = ["*", "@", ";", ":", "!", "\"", "?", "«", "»"]
symbol = [".", ","]
symbols = ",."
big_words = []

filename = "europarl-v7.da-en.da"
with open(filename, "r", encoding="UTF-8") as file:
    lines = file.readlines()

result = [line.split() for line in lines]

step_rate = 5
result2 = []
for i in range(0, len(lines),step_rate):
    result2.append((' '.join(lines[i:i+step_rate])).split())

# Changing to six words scope
left_scope = 15
right_scope = 10
middle = left_scope

print("Result 1: ", len(result))
print("Result 2: ", len(result2))
old_big_words = result[:500000]


# add padding
big_words_lsts = []
for i in tqdm(range(len(old_big_words))):
    lst = old_big_words[i]
    lst = ["<PAD>"]*left_scope + lst + ["<PAD>"]*right_scope
    big_words_lsts.append(lst)

for i in tqdm(range(len(big_words_lsts))):
    big_words = big_words_lsts[i]
    for x in range(len(big_words)-(left_scope+right_scope)+1):
        four_words = big_words[x:x+left_scope+right_scope]
        if any([x == y for y in char for x in four_words]):
            continue
        elif four_words[middle][-1] == symbol[1]:
            output1 = 1
        else:
            output1 = 0
        if "<PAD>" in four_words:
            if (four_words[0] != "<PAD>" and four_words[-1] != "<PAD>"):
                print("x")
                continue
        four_words = [x.strip(symbols) for x in four_words]
        big_lst.append((" ".join(four_words)).lower())
        output1_lst.append(output1)

os.chdir(current_dir)
df = pd.DataFrame()
df["comment_text"] = big_lst
df["label"] = output1_lst

print(len(df))
# df = df[:10000000]

def distribution(df):
    print(df["label"].value_counts())

distribution(df)
print(len(df))
header = ["comment_text", "label"]
df.to_csv("Datasets/EuroparlPad15-5_NoFullStop.csv", encoding="UTF-8", index=False, sep=";")