import os
import pandas as pd
from tqdm import tqdm

current_dir = os.getcwd()
os.chdir("/Users/lucasvilsen/Downloads/dagw/sektioner/danavis")
all_files = os.listdir(os.curdir)
print("Antal filer: ", len(all_files))
big_lst = []
output1_lst = []
char = ["*", "@", ";", ":", "!", "\"", "?", "«", "»"]
symbol = [".", ","]
big_words = []

print("3 processes needed: ")

# remember to change the range.
# up to 500 already used

last_upper = 500

lower = 500
upper = 500
if lower < last_upper:
    raise ValueError("lower bound needs to be bigger than the last upper, \n so that no files are used twice")

for i in tqdm(range(lower,upper)):
    current_big_words = ["<PAD> "]
    with open(all_files[i], "r", encoding="UTF-8") as file:
        for line in file.readlines():
            for word in line.split():
                big_words.append(word)


# Changing to six words scope
scope = 6
middle = int(scope/2)
padding = int(scope/2-1)

old_big_words = big_words


# add padding
big_words = []
for word in tqdm(old_big_words):
    if word[-1] == ".":
        for _ in range(padding):
            big_words.append("<PAD>")
        big_words.append(word)
        for _ in range(padding):
            big_words.append("<PAD>")
    else:
        big_words.append(word)

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
df = df[:600000]


header = ["comment_text", "label"]
df.to_csv("Datasets/DanavisDFwithPadding-1000:.csv", encoding="UTF-8", index=False)