import os
import pandas as pd

current_dir = os.getcwd()
os.chdir("/Users/lucasvilsen/Downloads/dagw/sektioner/tv2r")
all_files = os.listdir(os.curdir)
output1_lst = []
char = ["*", "@", ";", ":", "!", "\"", "?", "«", "»"]
symbol = [".", ",", ":"]
big_words = []
dataset = []
padding = "<PAD>"

def build_dataset(sentence):
    block_size = 8 # amount of previous characters to determine next
    X = []
    words = sentence.lower().split(" ")
    context = [padding] * block_size
    for i in range(len(words) + block_size):
        X.append(context)
        next_word = padding if i > len(words)-1 else words[i]
        context = context[1:] + [next_word] # crop context and append next character
    return X


for i in range(len(all_files) // 4):
    print("opening: " + all_files[i])
    if all_files[i] == ".DS_Store":
        continue
    lines = open(all_files[i], "r").read().splitlines()
    big_words += lines
dataset = build_dataset(" ".join(big_words))

print(len(dataset))
    
os.chdir(current_dir)
df = pd.DataFrame(dataset)
df.to_csv("Datasets/tv2DF.csv", encoding="UTF-8", index=False)
print("done")
