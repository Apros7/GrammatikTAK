import os
import pandas as pd
from tqdm import tqdm
import pickle

os.chdir("/Users/lucasvilsen/Desktop/GrammatikTAK/Datasets/")
filename = "europarl-v7.da-en.da"
with open(filename, "r", encoding="UTF-8") as file:
    lines = file.readlines()
with open("nutids_r_bøjninger.pickle", "rb") as f:
    nutids_r_bøjninger = pickle.load(f)
with open("nutids_r_stem.pickle", "rb") as f:
    nutids_r_stem = pickle.load(f)

df = pd.read_csv("../Datasets/EuroparlSentToPos.csv", encoding="UTF-8", sep=";")
sent = list(df["sent"])
pos = list(df["pos"])
print("DF len: ", len(df))


import stanza

pos_model = stanza.Pipeline("da", processors='tokenize,pos', use_gpu=True, cache_directory='./cache', tokenize_pretokenized=True, n_process=8)

def get_pos_tags(words):
    doc = pos_model(" ".join(words))
    results = [word.upos for sentence in doc.sentences for i, word in enumerate(sentence.words)]
    return results

import concurrent.futures

chunk_size = 2000

for i in tqdm(range(300000, 350000, chunk_size)):
    chunk = lines[i:i+chunk_size]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(lambda line: get_pos_tags(line.split()), chunk))
    for j, tags in enumerate(results):
        true_words = chunk[j].split()
        relative_pos = tags
        sent.append(" ".join(true_words))
        pos.append(" ".join(relative_pos))

df = pd.DataFrame(zip(sent, pos), columns=["sent", "pos"])
df.to_csv("../Datasets/EuroparlSentToPos.csv", encoding="UTF-8", index=False, sep=";")
print(df.head())