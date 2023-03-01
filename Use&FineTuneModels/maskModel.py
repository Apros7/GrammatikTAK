# https://huggingface.co/tasks/fill-mask
# Could potentially train own model or use pretrained danish model for mask

from transformers import pipeline

# Load the pre-trained Danish language model
model_name = "Maltehb/danish-bert-botxo"
fill_mask = pipeline("fill-mask", model=model_name)

def mask_model_words(sentence):
    words = sentence.split()
    lst = list()
    for i in range(len(words)):
        masked_words = words.copy()
        masked_words[i] = "[MASK]"
        masked_sentence = " ".join(masked_words)
        lst.append(masked_sentence)
    predictions = fill_mask(lst)

    # Extract the predicted tokens for each word
    lst = []
    for i, pred in enumerate(predictions):
        word_preds = []
        for p in pred[:3]:
            word_preds.append(p["token_str"])
        lst.append(word_preds)
    return lst

sentence = "hej jeg hedde lucas og jeg er ik seej."
words = sentence.split()

predictions = mask_model_words(sentence)

for i in range(len(words)):
    print("Word: ", words[i], ". And predictions are: ", predictions[i])

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
