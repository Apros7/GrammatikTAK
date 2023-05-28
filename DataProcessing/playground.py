import pickle
import os

os.chdir("/Users/lucasvilsen/Desktop/GrammatikTAK/GrammatiktakBackend")

dictionary = pickle.load(open("Datasets/dictionary.pickle", "rb"))

print(dictionary[:10])
print("heder" in dictionary)