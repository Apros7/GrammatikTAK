import chromadb
import numpy as np
import os
from dotenv import load_dotenv
import openai
import time

def get_embedding(list_of_text: list[str], model="text-embedding-ada-002", **kwargs) -> list[list[float]]:
    assert len(list_of_text) <= 2048, "The batch size should not be larger than 2048."
    # replace newlines, which can negatively affect performance.
    list_of_text = [text.replace("\n", " ") for text in list_of_text]
    data = openai.embeddings.create(input=list_of_text, model=model, **kwargs).data
    return [d.embedding for d in data]


def load_embeddings(path):
    loaded_data = np.load(path)
    embedded_words = loaded_data['arr_0']
    embedded_vectors = loaded_data['arr_1']
    return embedded_words, embedded_vectors

## CODE ##

load_dotenv()
openai_client = openai.OpenAI()

path_to_embeddings = "/Users/lucasvilsen/Desktop/GrammatikTAK/DataProcessing/SpellcheckerEmbeddings/arrays"
latest_embedding = "20231122_195118.npz"
path_to_latest_embedding = os.path.join(path_to_embeddings, latest_embedding)
embedded_words, embedded_vectors = load_embeddings(path_to_latest_embedding)
print("Size: ", len(embedded_words), "/400000")

chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="grammatiktak-spellchecking")

collection.add(
    embeddings=[list(a) for a in embedded_vectors],
    documents=list(embedded_words),
    ids=list(embedded_words)
)

start_time = time.time()
print("started_timer")
word_to_test = "inmad"
word_to_test_embedding = get_embedding(word_to_test)[0]
predictions = collection.query(
    query_embeddings=word_to_test_embedding,
    n_results=50
)
print("time taken: ", time.time() - start_time)

print("Word to predict: ", word_to_test)
print("Best 5 guesses: ", *list(predictions.items()), sep="\n")


