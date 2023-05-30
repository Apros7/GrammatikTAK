from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from torch.utils.data import DataLoader

model = AutoModelForSeq2SeqLM.from_pretrained("Maltehb/danish-bert-botxo")