import torch
from transformers import Trainer

class Dataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels=None):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        if self.labels:
            item["labels"] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.encodings["input_ids"])

def load_model(model_path):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    torch.device(device)
    punctuation_model = torch.load(model_path, map_location=torch.device(device))
    punctuation_model.eval()
    punctuation_model.to(device)
    punctuation_trainer = Trainer(punctuation_model)
    return punctuation_trainer