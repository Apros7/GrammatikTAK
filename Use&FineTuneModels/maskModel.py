# https://huggingface.co/tasks/fill-mask
# Could potentially train own model or use pretrained danish model for mask

from transformers import pipeline

# Load the pre-trained Danish language model
model_name = "Maltehb/danish-bert-botxo"
fill_mask = pipeline("fill-mask", model=model_name)

# Input sentence with a mask token
input_sentence = "Hej mit [MASK] er Lucas"

# Use the model to predict the missing word
predictions = fill_mask(input_sentence)

# Print the top 5 predictions with their scores
for pred in predictions[:5]:
    print(pred["token_str"], pred["score"])
