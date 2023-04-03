import os
import pandas as pd
from tqdm import tqdm

current_dir = os.getcwd()
#os.chdir("/Users/lucasvilsen/Downloads/dagw/sektioner/danavis")
os.chdir("/Users/lucasvilsen/Downloads/dagw/sektioner/tv2r")
all_files = os.listdir(os.curdir)
print("Antal filer: ", len(all_files))
big_lst = []
output1_lst = []
char = ["*", "@", ";", ":", "!", "\"", "?", "«", "»"]
symbol = [".", ","]
symbols = ",."
big_words = []

# remember to change the range.
# up to 500 already used

last_upper = 0

lower = 0
upper = 5000


print(f"3 processes needed: ")


if lower < last_upper:
    raise ValueError("lower bound needs to be bigger than the last upper, \n so that no files are used twice")

for i in tqdm(range(lower,upper)):
    current_big_words = []
    with open(all_files[i], "r", encoding="UTF-8") as file:
        for line in file.readlines():
            for word in line.split():
                current_big_words.append(word)
    big_words.append(current_big_words)


# Changing to six words scope
scope = 6
middle = int(scope/2)
padding = int(scope/2-1)

old_big_words = big_words


# add padding
big_words_lsts = []
for i in tqdm(range(len(old_big_words))):
    lst = old_big_words[i]
    lst = ["<PAD>"]*padding + lst + ["<PAD>"]*padding
    big_words_lsts.append(lst)

for i in tqdm(range(len(big_words_lsts))):
    big_words = big_words_lsts[i]
    for x in range(len(big_words)-3):
        four_words = big_words[x:x+scope]
        if any([x == y for y in char for x in four_words]):
            continue
        elif four_words[middle][-1] == symbol[1]:
            output1 = 1
        else:
            output1 = 0
        four_words = [x.strip(symbols) for x in four_words]
        big_lst.append((" ".join(four_words)).lower())
        output1_lst.append(output1)

os.chdir(current_dir)
df = pd.DataFrame()
df["comment_text"] = big_lst
df["label"] = output1_lst
df = df

def distribution(df):
    print(df["label"].value_counts())


distribution(df)
header = ["comment_text", "label"]
df.to_csv("Datasets/TV2withPadding1.csv", encoding="UTF-8", index=False, sep=";")