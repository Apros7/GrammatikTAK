import os
import pandas as pd
import re
import stanza
from tqdm import tqdm
import lemmy
import time

pos_model = stanza.Pipeline("da", processors='tokenize,pos', use_gpu=True, cache_directory='./cache', tokenize_pretokenized=True, n_process=4)
lemmatizer = lemmy.load("da")

current_dir = os.getcwd()
os.chdir("/Users/lucasvilsen/Downloads/dagw/sektioner/tv2r")
all_files = os.listdir(os.curdir)
output1_lst = []

def get_pos(sentence):
    doc = pos_model(sentence)
    return [word.upos for sentence in doc.sentences for word in sentence.words]


def build_dataset():
    sentences = get_sentences()
    dataset = []
    pos_cache = {}
    lemmatizer = lemmy.load("da")
    print(len(sentences))
    for x in tqdm(range(0, len(sentences), 5)):
        cur_sentences = sentences[x:x+100]
        cur_sentence = " ".join(cur_sentences)
        words = cur_sentence.split()
        len_cur_sent = len(words)
        try:
            pos = pos_cache[cur_sentence]
        except KeyError:
            pos = get_pos(cur_sentence)
            pos_cache[cur_sentence] = pos
        if len(pos) != len(words):
            continue
        for i, word in enumerate(words):
            if pos[i] == "VERB": 
                if i < 4:
                    words_after = ["<pad>"]*(4-i) + words[0:i+5]
                    words_before = ["<pad>"]*(4-i) + words[0:i] + [lemmatizer.lemmatize(pos[i], word)[0]] + words[i+1:i+5]
                elif i > len_cur_sent-4:
                    words_after = words[i-4:] + ["<pad>"]*(len_cur_sent-i)
                    words_before = words[i-4:i] + [lemmatizer.lemmatize(pos[i], word)[0]] + words[i+1:] + ["<pad>"]*(len_cur_sent-i)
                else:
                    words_after = words[i-4:i+5]
                    words_before = words[i-4:i] + [lemmatizer.lemmatize(pos[i], word)[0]] + words[i+1:i+5]
                dataset.append([(" ".join(words_before)).lower(), (" ".join(words_after)).lower()])
                if len(words_before) != 9:
                    continue
    return dataset


# to all_files[:100] already converted
print(len(all_files))

def get_sentences():
    sentences = []
    for i in range(len(all_files[:100])):
        filepath = all_files[i]
        with open(filepath, "r") as f:
            lines = f.readlines()
            lines = [line.strip() for line in lines]
            lines = [line.split(".") for line in lines]
            lines = [item for sublist in lines for item in sublist if item]
            sentences += lines
    return sentences

dataset = build_dataset()

print(len(dataset))
    
os.chdir(current_dir)
df = pd.DataFrame(dataset)
os.chdir("/Users/lucasvilsen/Desktop/GrammatikTAK/GrammatiktakDatasets/")
df.to_csv(f"otherDatasets/LemmatizedSentToTenseSent/{time.time()}", encoding="UTF-8", index=False, header=False, sep=";")
