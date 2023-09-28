# Desktop/GrammatikTAK/FineTuneModels/CommaModels/SaveDistilBert.py

import torch


model = torch.load("commaDistilBERT1.pt")

from transformers import TrainingArguments, Trainer, DistilBertForSequenceClassification
DistilBertForSequenceClassification.save_pretrained(model, "commaDistilBERTcorrect.pt")