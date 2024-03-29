import string
import pandas as pd
from tqdm import tqdm
import os
import pickle

current_dir = os.getcwd()
# Desktop/GrammatikTAK/DataProcessing/CommaDataset/sent_to_label_revisited.py
os.chdir("/Users/lucasvilsen/Desktop/GrammatikTAK/Datasets/")

#/Users/lucasvilsen/Desktop/GrammatikTAK/Datasets/europarl-v7.da-en.da

filename = "europarl-v7.da-en.da"
with open(filename, "r", encoding="UTF-8") as file:
    lines = file.readlines()

print(len(lines))

# lines = [lines[1]]
# Change this:
number_of_rtx_6000_gpus = 8
possible_per_rtx_6000_gpu = 240000
# lines = lines[:10000]

print(len(lines))

TRANSLATION_TABLE_WITH_COMMA = str.maketrans('', '', string.punctuation)
TRANSLATION_TABLE_WITHOUT_COMMA = str.maketrans('', '', string.punctuation.replace(",", "").replace(".", ""))

cleaned_lines = [line.replace(" -", ",").lower() for line in tqdm(lines) if len(line.translate(TRANSLATION_TABLE_WITHOUT_COMMA).strip()) > 0]
lines_with_comma = [line.translate(TRANSLATION_TABLE_WITHOUT_COMMA).strip().replace("  ", " ") for line in tqdm(cleaned_lines)]

PADDING_LEFT = 15
PADDING_RIGHT = 5

lines_with_padding = [PADDING_LEFT * ["<PAD>"] + line.split() + PADDING_RIGHT * ["<PAD>"] for line in lines_with_comma]
labels = []
cleaned_dataset = []

for i in tqdm(range(len(lines_with_padding))):
    for j in range(len(lines_with_padding[i])-(PADDING_LEFT+PADDING_RIGHT)+1):
        sample = lines_with_padding[i][j:j+PADDING_LEFT+PADDING_RIGHT]
        if sample[PADDING_LEFT-1][-1] == ",": middle_word_punc = 1
        elif sample[PADDING_LEFT-1][-1] == ".": middle_word_punc = 2
        else: middle_word_punc = 0
        cleaned_dataset.append((" ".join(sample)).replace(",", "").replace(".", ""))
        labels.append(middle_word_punc)
        
df = pd.DataFrame()
df["data"] = cleaned_dataset
df["label"] = labels

def distribution(df):
    print(df["label"].value_counts())

distribution(df)
print(len(df))

# print(*[(d, p) for d, p in zip(cleaned_dataset[:100], labels[:100])], sep="\n")

# df = df[:1000]
df.to_csv("SentToLabel_15-5_Revisited.csv", encoding="UTF-8", index=False, sep=";")
# df.to_csv("SentToLabel_15-10_Revisited_test.csv", encoding="UTF-8", index=False, sep=";")

# with open("SentToLabel_15-5_Revisited.pickle") as file:
#     pickle.dump(df, file)