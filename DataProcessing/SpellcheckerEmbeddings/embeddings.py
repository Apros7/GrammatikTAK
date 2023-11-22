from tqdm import tqdm
from dotenv import load_dotenv
import openai
import pickle
import pandas as pd
import time
import json
import numpy as np
import datetime
import os

load_dotenv()
openai_client = openai.OpenAI()

## UTILS ## 

OPENAI_VECTOR_SIZE = 1536
MAX_BATCH_SIZE = 2000

def get_embeddings(list_of_text: list[str], model="text-embedding-ada-002", **kwargs) -> list[list[float]]:
    assert len(list_of_text) <= 2048, "The batch size should not be larger than 2048."
    # replace newlines, which can negatively affect performance.
    list_of_text = [text.replace("\n", " ") for text in list_of_text]
    data = openai.embeddings.create(input=list_of_text, model=model, **kwargs).data
    return np.array([d.embedding for d in data])

def save_embeddings(embedded_words, embedded_vectors, path):
    path_with_date = os.path.join(path, datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
    np.savez_compressed(path_with_date, embedded_words, embedded_vectors)

def load_embeddings(path):
    loaded_data = np.load(path)
    embedded_words = loaded_data['arr_0']
    embedded_vectors = loaded_data['arr_1']
    return embedded_words, embedded_vectors

def update_embedding_words_and_vectors(embedded_words, embedded_vectors, batch_words, batch_embeddings):
    embedded_words = np.concatenate((embedded_words, batch_words))
    embedded_vectors = np.concatenate((embedded_vectors, batch_embeddings), axis=0)
    return embedded_words, embedded_vectors

def run_batch(words_without_embedding, embedded_words, embedded_vectors, path):
    batch_words = words_without_embedding[:MAX_BATCH_SIZE]
    words_without_embedding = words_without_embedding[MAX_BATCH_SIZE:]
    batch_embeddings = get_embeddings(batch_words)
    embedded_words, embedded_vectors = update_embedding_words_and_vectors(embedded_words, embedded_vectors, batch_words, batch_embeddings)
    save_embeddings(embedded_words, embedded_vectors, path)
    words_remaining = len(words_without_embedding)
    if words_remaining > 0: print(f"Words to embed remaining: {words_remaining} - size of embedding cache: {len(embedded_vectors), len(embedded_words)}")
    return words_without_embedding, embedded_words, embedded_vectors

def get_words_without_embeddings(words, embedded_words):
    words_set = set(words)
    embedding_cache_set = set(embedded_words)
    elements_not_in_dict = list(words_set - embedding_cache_set)
    return np.array(elements_not_in_dict)

## RUNNING ##

print("Loaded")

path = "/Users/lucasvilsen/Desktop/GrammatikTAK/DataProcessing/SpellcheckerEmbeddings/arrays"
path_to_latest_embeddings = "/Users/lucasvilsen/Desktop/GrammatikTAK/DataProcessing/SpellcheckerEmbeddings/arrays/20231122_194259.npz"

words = sorted(pickle.load(open("/Users/lucasvilsen/Desktop/GrammatikTAK/Datasets/dictionary.pickle", "rb")))
# embedded_words = np.array([])
# embedded_vectors = embedded_words.reshape(0, OPENAI_VECTOR_SIZE)
embedded_words, embedded_vectors = load_embeddings(path_to_latest_embeddings)
words_without_embedding = get_words_without_embeddings(words, embedded_words)

batches_to_run = len(words_without_embedding) // MAX_BATCH_SIZE
print("Estimated batches to run: ", batches_to_run)

print("Ready to run")
for _ in tqdm(range(10)):
    words_without_embedding, embedded_words, embedded_vectors = run_batch(words_without_embedding, embedded_words, embedded_vectors, path)