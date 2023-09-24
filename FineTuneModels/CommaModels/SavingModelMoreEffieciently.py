import torch
import os

os.chdir("/Users/lucasvilsen/Desktop")

device = "mps"
torch.device(device)
model = torch.load("commaDistilBERT1", map_location=torch.device('cpu'))
model.to(device)
model.eval()

os.chdir("/Users/lucasvilsen/Desktop/GrammatikTAK/FineTuneModels/CommaModels")
model.save_pretrained("CommaDistilBert1.config")

# To load:
from transformers import TrainingArguments, Trainer, BertForSequenceClassification
model = BertForSequenceClassification.from_pretrained("CommaDistilBert1.config")

# Same size, yikes
