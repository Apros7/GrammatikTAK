import os
import pandas as pd
import re
import stanza
from tqdm import tqdm
import time
import numpy as np

pos_model = stanza.Pipeline("da", processors='tokenize,pos,lemma', use_gpu=True, cache_directory='./cache', tokenize_pretokenized=True, n_process=4)

current_dir = os.getcwd()
os.chdir("/Users/lucasvilsen/Downloads/dagw/sektioner/tv2r")
all_files = os.listdir(os.curdir)
output1_lst = []

def get_pos(sentence):
    doc = pos_model(sentence)
    return [word.upos for sentence in doc.sentences for word in sentence.words], [word.lemma for sentence in doc.sentences for word in sentence.words]

def build_dataset(number_of_files, sentences = None):
    upper = None
    if sentences is None:
        sentences, upper = get_sentences(number_of_files)
    dataset = []
    step_rate = 5
    for x in tqdm(range(0, len(sentences), step_rate)):
        cur_sentences = sentences[x:x+5]
        cur_sentence = " ".join(cur_sentences)
        words = cur_sentence.split()
        pos, lemma = np.array(get_pos(cur_sentence))
        verb_indices = np.where(pos == "VERB")[0]
        if len(pos) != len(words):
            continue
        for i in verb_indices:
            words_after = words[i].strip(".,!?;:")
            if i < 4:
                words_before = ["<pad>"]*(4-i) + words[0:i] + [lemma[i]]
            else:
                words_before = words[i-4:i] + [lemma[i]]
            words_before_len = len(words_before)
            words_before = (" ".join(words_before)).strip(".,!?;:").lower()
            dataset.append([words_before, (words_after).lower()])
            if words_before_len != 5:
                print("Error:")
                print(i)
                print(words_before)
                continue
    return dataset, upper

print(len(all_files))

def get_lower():
    os.chdir("/Users/lucasvilsen/Desktop/GrammatikTAK/GrammatiktakDatasets/")
    with open("getDatasets/make_tense_last_interval.txt", "r") as f:
        lower = int(f.read())
    return lower

def get_sentences(number_of_files):
    lower = get_lower()
    upper = lower + number_of_files
    print("reading in this interval: ", lower, " - ", upper-1, " (both included)")
    if upper > len(all_files):
        upper = len(all_files)
        print("Vi overskrider mængden af filer. Dermed er det {} filer.".format(len(all_files)-lower))
    sentences = []
    os.chdir("/Users/lucasvilsen/Downloads/dagw/sektioner/tv2r")
    for i in range(lower, upper):
        filepath = all_files[i]
        try: lines = open(filepath, "r").readlines()
        except: print("Error: ", filepath); continue; #error with .DS_Store
        lines = [line.strip() for line in lines]
        lines = [line.split(".") for line in lines]
        lines = [item for sublist in lines for item in sublist if item]
        sentences += lines
    return sentences, upper

def save_dataset(dataset, upper=None):
    print(len(dataset))
    os.chdir(current_dir)
    df = pd.DataFrame(dataset)
    os.chdir("/Users/lucasvilsen/Desktop/GrammatikTAK/GrammatiktakDatasets/")
    if upper is not None:
        with open("getDatasets/make_tense_last_interval.txt", "w") as f:
            print("gemmer: ", str(upper))
            f.write(str(upper))
    df.to_csv(f"otherDatasets/LemmatizedSentToTenseSent/{time.time()}", encoding="UTF-8", index=False, header=False, sep=";")
    print("Dataset saved")

# size of dataset:
size = 3000

# 1000 => about 25000 lines: about 22 minutes

dataset, upper = build_dataset(size)
save_dataset(dataset, upper)

    
