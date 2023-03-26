import os
import pandas as pd
import re
import stanza
from tqdm import tqdm
import lemmy
import time
import numpy as np

pos_model = stanza.Pipeline("da", processors='tokenize,pos', use_gpu=True, cache_directory='./cache', tokenize_pretokenized=True, n_process=4)
lemmatizer = lemmy.load("da")

current_dir = os.getcwd()
os.chdir("/Users/lucasvilsen/Downloads/dagw/sektioner/tv2r")
all_files = os.listdir(os.curdir)
output1_lst = []

def get_pos(sentence):
    doc = pos_model(sentence)
    return [word.upos for sentence in doc.sentences for word in sentence.words]

def build_dataset(lower, upper):
    sentences = get_sentences(lower, upper)
    dataset = []
    print(len(sentences))
    for x in tqdm(range(0, len(sentences), 5)):
        cur_sentences = sentences[x:x+100]
        cur_sentence = " ".join(cur_sentences)
        words = cur_sentence.split()
        len_cur_sent = len(words)
        pos = np.array(get_pos(cur_sentence))
        verb_indices = np.where(pos == "VERB")[0]
        if len(pos) != len(words):
            continue
        for i in verb_indices:
            if i < 4:
                words_after = ["<pad>"]*(4-i) + words[0:i+5]
                words_before = ["<pad>"]*(4-i) + words[0:i] + [lemmatizer.lemmatize(pos[i], words[i])[0]] + words[i+1:i+5]
                value = 1
            elif i >= len_cur_sent-4:
                words_after = words[i-4:] + ["<pad>"]*(4-(len_cur_sent-i)+1)
                words_before = words[i-4:i] + [lemmatizer.lemmatize(pos[i], words[i])[0]] + words[i+1:] + ["<pad>"]*(4-(len_cur_sent-i)+1)
                value = 2
            else:
                words_after = words[i-4:i+5]
                words_before = words[i-4:i] + [lemmatizer.lemmatize(pos[i], words[i])[0]] + words[i+1:i+5]
                dataset.append([(" ".join(words_before)).lower(), (" ".join(words_after)).lower()])
                value = 3
            if len(words_before) != 9:
                print("Error:")
                print(words_before, value)
                print(i, len_cur_sent)
                continue
    return dataset


# to all_files[:300] already converted
print(len(all_files))

def get_sentences(lower, upper):
    sentences = []
    for i in range(len(all_files[lower:upper])):
        filepath = all_files[i]
        with open(filepath, "r") as f:
            lines = f.readlines()
            lines = [line.strip() for line in lines]
            lines = [line.split(".") for line in lines]
            lines = [item for sublist in lines for item in sublist if item]
            sentences += lines
    return sentences

def save_dataset(dataset):
    print(len(dataset))
    os.chdir(current_dir)
    df = pd.DataFrame(dataset)
    os.chdir("/Users/lucasvilsen/Desktop/GrammatikTAK/GrammatiktakDatasets/")
    df.to_csv(f"otherDatasets/LemmatizedSentToTenseSent/{time.time()}", encoding="UTF-8", index=False, header=False, sep=";")
    print("Dataset saved")

dataset = build_dataset(201, 300)
save_dataset(dataset)
    
