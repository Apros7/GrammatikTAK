import os
import pandas as pd
from transformers import pipeline
import pickle
import random

os.chdir("/Users/lucasvilsen/Desktop/GrammatikTAK/Datasets/")

with open("NerHuman.pickle", "rb") as file:
    df = pickle.load(file)

sentences = list(df["sentence"].values)
ner = list(df["ner"].values)

print(df)

filename = "europarl-v7.da-en.da"
with open(filename, "r", encoding="UTF-8") as file:
    lines = file.readlines()

random.seed(4242)
random.shuffle(lines)

ner_model = pipeline(task='ner', model='saattrupdan/nbailab-base-ner-scandi', aggregation_strategy='first')

os.chdir("/Users/lucasvilsen/Desktop/GrammatikTAK/DataProcessing/nerDataset/")
index = int(open("ner_index.txt", "r", encoding="UTF-8").readline())
print("Starting at index: ", index)

def save_index(index, plus_one=False):
    if plus_one:
        index += 1
    print(str(index))
    os.chdir("/Users/lucasvilsen/Desktop/GrammatikTAK/DataProcessing/nerDataset/")
    with open("ner_index.txt", "w", encoding="UTF-8") as file:
        file.write(str(index))
    return index

for line in lines[index:]:
    result = ner_model(line)
    namedEntities = [row["word"].replace(" - ", "-") for row in result]
    if len(namedEntities) == 0:
        index = save_index(index, plus_one=True)
        continue
    print(line)
    human_response = "buffer"

    while human_response not in ["quit", "", "skip"]:
        print(namedEntities)
        human_response = input("Please validate (help for more info): \n")
        if human_response == "help":
            print("Press enter if correct\nType quit to exit\nSkip to skip current line")
            print("Add _word_ to add a word\nDel _index_number_ to delete a word from ner\n")
        elif human_response[:3] == "add":
            namedEntities.append(human_response[4:])
        
        elif human_response[:3] == "del":
            try: int(human_response[4:])
            except: print("Not a number")
            del namedEntities[int(human_response[4:])]

    if human_response == "quit":
        index = save_index(index, plus_one=False)
        break
    
    if human_response == "skip":
        index = save_index(index, plus_one=True)
        continue
    
    if human_response == "":
        sentences.append(line)
        ner.append(namedEntities)
    
    index = save_index(index, plus_one=True)

os.chdir("/Users/lucasvilsen/Desktop/GrammatikTAK/Datasets/")
df = pd.DataFrame(zip(sentences, ner), columns=["sentence", "ner"])
print("Number of sentences annotated: ", len(df))
print(df)
with open("NerHuman.pickle", "wb") as file:
    pickle.dump(df, file)