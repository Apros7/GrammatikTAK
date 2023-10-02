import sys 
sys.path.append("/Users/lucasvilsen/Desktop/GrammatikTAK")

from GrammatiktakBackend.Utilities.model_utils import DistilBertForPunctuation
from sklearn.metrics import accuracy_score
import pandas as pd

def decode_dateset(dataset : list, labels : list):
    sentences, words, new_labels = [], [], []
    for i, d in enumerate(dataset):
        if d.split()[14] != "<PAD>": words.append(d.split()[14]); new_labels.append(labels[i])
        else: sentences.append(" ".join(words)); words = []
    sentences.append(" ".join(words))
    return sentences, new_labels

if __name__ == "__main__":
    model = DistilBertForPunctuation(path = "/Users/lucasvilsen/Desktop/GrammatikTAK/GrammatiktakBackend/models/commaDistilBERTcorrect")
    dataset = pd.read_csv("Datasets/SentToLabel_15-10_Revisited_test.csv", sep=";")
    dataset = dataset[:20000]
    lines = dataset["data"].to_list()
    labels = dataset["label"].to_list()
    sent, labels = decode_dateset(lines, labels)
    predictions = model.get_predictions(sent)
    # print(*lines, sep="\n")
    # print("Made dataset: ")
    # print(*model.get_dataset(sent), sep="\n")
    # print("Predictions:", *[(l, p) for l, p in zip(labels, predictions)], sep="\n")
    accuracy = accuracy_score(labels, predictions)
    print("Accuracy all       : ", round(accuracy * 100, 2))
    labels_and_predictions = [(l, p) for l, p in zip(labels, predictions) if p != 2 and l != 2]
    accuracy = accuracy_score([x[0] for x in labels_and_predictions], [x[1] for x in labels_and_predictions])
    print("Accuracy only comma: ", round(accuracy * 100, 2))

    