import os
import pandas as pd
import re
import stanza
from tqdm import tqdm
import lemmy

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
    print(len(sentences))
    for x in tqdm(range(0, len(sentences), 100)):
        cur_sentences = sentences[x:x+100]
        for i in range(len(cur_sentences)):
            cur_sentence = cur_sentences[i]
            pos = get_pos(cur_sentence)
            words_before = cur_sentence.split()
            words_after = cur_sentence.split()
            if len(pos) != len(words_before):
                continue
            for i, word in enumerate(words_before):
                if pos[i] == "VERB":
                    words_before[i] = lemmatizer.lemmatize(pos[i], word)[0]
            dataset.append([" ".join(words_before), " ".join(words_after)])
    return dataset

def get_sentences():
    new_lines = []
    for i in range(len(all_files[:100])):
        lines = open(all_files[i], "r").read().splitlines()
        for line in lines:
            sentences = re.split("(?<=[.!?])\s+(?=[A-Z0-9])", line)
            new_lines += sentences
    return new_lines

dataset = build_dataset()

print(len(dataset))
    
os.chdir(current_dir)
df = pd.DataFrame(dataset)
print(df.head())
os.chdir("/Users/lucasvilsen/Desktop/GrammatikTAK/GrammatiktakDatasets/")
df.to_csv("uncheckedDatasets/LemmatizedSentToTenseSent", encoding="UTF-8", index=False, header=False, sep=";")
print("done")
