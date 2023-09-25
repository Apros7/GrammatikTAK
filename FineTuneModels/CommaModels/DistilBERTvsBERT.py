## Testing my best bert vs best distil bert in time and accuracy

from transformers import AutoTokenizer, Trainer, BertTokenizer
import torch
import pandas as pd
import numpy as np
import os
from sklearn.metrics import accuracy_score
import time

os.chdir("/Users/lucasvilsen/Desktop/GrammatikTAK/Datasets")

# data_size = 20000

# df15_5 = pd.read_csv("SentToLabel_15-5_Revisited.csv", sep=";")
# df_distil = df15_5[-data_size:]
# df_distil.to_csv("SentToLabel_15-5_Revisited_20000.csv", sep=";")

# print("Loaded data")

# df15_10 = pd.read_csv("SentToLabel_15-10_Revisited.csv", sep=";")
# df_bert = df15_10[-data_size:]
# df_bert.to_csv("SentToLabel_15-10_Revisited_20000.csv", sep=";")

df_distil = pd.read_csv("SentToLabel_15-5_Revisited_20000.csv", sep=";")
df_bert = pd.read_csv("SentToLabel_15-10_Revisited_20000.csv", sep=";")

print(df_distil.head(10))

print("Loaded data")

data_bert = df_bert["data"].to_list()
labels_bert = df_bert["label"].to_list()

data_distil = df_distil["data"].to_list()
labels_distil = df_distil["label"].to_list()

batch_size = 32

class CustomDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels=None, batch_size=16):
        self.encodings = encodings
        self.labels = labels
        self.batch_size = batch_size

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        if self.labels:
            item["labels"] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.encodings["input_ids"])

os.chdir("/Users/lucasvilsen/Desktop")

def load_model(model_path):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    torch.device(device)
    punctuation_model = torch.load(model_path, map_location=torch.device(device))
    punctuation_model.eval()
    punctuation_model.to(device)
    punctuation_trainer = Trainer(punctuation_model)
    return punctuation_trainer

bert_path = "GrammatikTAK/GrammatiktakBackend/models/commaModel10"
distil_bert_path = "commaDistilBERT1"

bert_tokenizer = BertTokenizer(vocab_file="GrammatikTAK/GrammatiktakBackend/models/vocab.txt", do_lower_case=False)
distil_tokenizer = AutoTokenizer.from_pretrained("Geotrend/distilbert-base-da-cased")

bert = load_model(bert_path)
distil_bert = load_model(distil_bert_path)

print("Loaded models")

def evaluate_model(trainer, tokenizer, data, labels):
    print("Evaluating...")
    print("Parameters: ", trainer.model.num_parameters())
    start_time = time.time()
    with torch.no_grad():
        tokenized_data = tokenizer(data, padding=True, truncation=True)
        final_dataset = CustomDataset(tokenized_data)
        raw_predictions, _, _ = trainer.predict(final_dataset)
        true_predictions = np.argmax(raw_predictions, axis=1)
        accuracy = accuracy_score(labels, true_predictions)
    print("Time it took: ", time.time() - start_time)
    return accuracy

bert_accuracy = evaluate_model(bert, bert_tokenizer, data_bert, labels_bert)
print(f"Bert Accuracy: {bert_accuracy:.6f}")

distil_bert_accuracy = evaluate_model(distil_bert, distil_tokenizer, data_distil, labels_distil)
print(f"Distil Bert Accuracy: {distil_bert_accuracy:.6f}")

# Distil is worse and slower 
