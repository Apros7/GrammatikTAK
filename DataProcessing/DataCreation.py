import os
import pandas as pd

current_dir = os.getcwd()
os.chdir("/Users/lucasvilsen/Downloads/dagw/sektioner/danavis")
all_files = os.listdir(os.curdir)
big_lst = []
output1_lst = []
char = ["*", "@", ";", ":", "!", "\"", "?", "«", "»"]
symbol = [".", ","]
big_words = []

for i in range(1,len(all_files)-1):
    with open(all_files[i], "r", encoding="UTF-8") as file:
        for line in file.readlines():
            for word in line.split():
                big_words.append(word)
for x in range(len(big_words)-4):
    four_words = big_words[x:x+4]
    if any([x == y for y in char for x in four_words]):
        continue
    if four_words[2] == symbol[0]:
        output1 = 1
        four_words = big_words[x:x+5]
        four_words.remove(symbol[0])
    elif any([x == symbol[0] for x in four_words]):
        continue
    elif four_words[2] == symbol[1]:
        output1 = 2
        four_words = big_words[x:x+5]
        four_words.remove(symbol[1])
    elif any([x == symbol[1] for x in four_words]):
            continue
    else:
        output1 = 0
    big_lst.append((" ".join(four_words)).lower())
    output1_lst.append(output1)

os.chdir(current_dir)
df = pd.DataFrame()
df["comment_text"] = big_lst
df["label"] = output1_lst


header = ["comment_text", "label"]
df.to_csv("Datasets/DanavisDF.csv", encoding="UTF-8", index=False)