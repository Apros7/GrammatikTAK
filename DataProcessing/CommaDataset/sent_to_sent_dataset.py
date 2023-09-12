import os
import string
import pandas as pd
from tqdm import tqdm

current_dir = os.getcwd()
os.chdir("/Users/lucasvilsen/Desktop/GrammatikTAK/Datasets/")

filename = "europarl-v7.da-en.da"
with open(filename, "r", encoding="UTF-8") as file:
    lines = file.readlines()

TRANSLATION_TABLE_WITH_COMMA = str.maketrans('', '', string.punctuation)
TRANSLATION_TABLE_WITHOUT_COMMA = str.maketrans('', '', string.punctuation.replace(",", ""))

cleaned_lines = [line.replace(" -", ",").lower() for line in tqdm(lines) if len(line.translate(TRANSLATION_TABLE_WITHOUT_COMMA).strip()) > 0]
lines_with_comma = [line.translate(TRANSLATION_TABLE_WITHOUT_COMMA).strip().replace("  ", " ") for line in tqdm(cleaned_lines)]
lines_without_comma = [line.translate(TRANSLATION_TABLE_WITH_COMMA).strip().replace("  ", " ") for line in tqdm(cleaned_lines)]
print(len([x for x in lines_with_comma if len(x) == 0]))
print(len([x for x in lines_without_comma if len(x) == 0]))
print(lines[4])
print(lines_with_comma[4])
print(lines_without_comma[4])

df = pd.DataFrame()
df["withoutComma"] = lines_without_comma
df["withComma"] = lines_with_comma
df.to_csv("SentToSent.csv", encoding="UTF-8", index=False, sep=";")