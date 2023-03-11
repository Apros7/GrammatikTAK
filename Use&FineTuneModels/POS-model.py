from danlp.models import load_bert_ner_model
bert = load_bert_ner_model()
# Get lists of tokens and labels in BIO format
tokens, labels = bert.predict("Jens Peter Hansen kommer fra Danmark")
print(" ".join(["{}/{}".format(tok,lbl) for tok,lbl in zip(tokens,labels)]))

print("\n\n")

# To get a correct tokenization, you have to provide it yourself to BERT  by providing a list of tokens
# (for example SpaCy can be used for tokenization)
# With this option, output can also be choosen to be a dict with tags and position instead of BIO format
tekst_tokenized = ['Han', 'hedder', 'Anders', 'And', 'Andersen', 'og', 'bor', 'i', 'Århus', 'C']
print(bert.predict(tekst_tokenized, IOBformat=False))