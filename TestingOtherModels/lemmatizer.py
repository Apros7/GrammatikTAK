import lemmy

lemmatizer = lemmy.load("da")
print(*zip([lemmatizer.lemmatize("", word) for word in input.split()], input.split(), pos_tags), sep="\n")