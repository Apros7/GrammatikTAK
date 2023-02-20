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
    # pred["token_str"] is string

# add this to bottom of find_suggestions:
"""
    start = time.time()
    word2 = mask_model_word(word1 + " [MASK] " + word3)
    mask_model_time.append(time.time() - start)

    #print("NGRAM: got this word: ", word)
    #print("MASK:  got this word: ", word2)
    return word

model_name = "Maltehb/danish-bert-botxo"
fill_mask = pipeline("fill-mask", model=model_name)

def mask_model_word(sentence):
    predictions = fill_mask(sentence)
    lst = []
    for pred in predictions[:5]:
        lst.append(pred["token_str"])
    return lst
"""
