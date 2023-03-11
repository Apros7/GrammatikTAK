
test_data = ['fal', 'krit', 'skedt', 'fjord', 'julpet', 'egenlig', 'selvskab', 'redede', 
            'litter', 'cykkel', 'smøret', 'profesor', 'skuppede', 'længte', 'skyldede', 'pusse', 'soldt', 'sovn', ]
correct_data = ['fald', 'kridt', 'sket', 'fjor', 'hjulpet', 'egentlig', 'selskab', 'reddede', 
                'liter', 'cykel', 'smørret', 'professor', 'skubbede', 'længde', 'skyllede', 'pudse', 'solgt', 'sogn']

wrong_words = []
correct_words = []

import csv

misspelled_words = {}
failed = []

with open("DataProcessing/spelling_mistakes.csv", "r", newline="") as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row[0].split()) > 2:
            if len(row[0].split()) == 3:
                wrong_word = row[0].split()[0]
                correct_word = row[0].split()[1].strip("()") + " " + row[0].split()[2].strip("()")
                misspelled_words[wrong_word] = correct_word
                continue
            failed.append(row)
            continue
        wrong_word, correct_word = row[0].split()
        misspelled_words[wrong_word] = correct_word
        wrong_words.append(wrong_word)
        correct_words.append(correct_word.strip("()"))

print(len(misspelled_words.items()))

# sort failed
for i in range(len(failed)):
    print("Her er den fejlede linje: \n")
    print(failed[i])

    wrong_word = input("indtast det forkerte ord: (esc to skip)\n")
    if wrong_word == "esc":
        continue
    correct_word = input("indtast det rigtige ord: \n")
    print(f"Dermed ser det sådan ud: {wrong_word} -> {correct_word}")
    add = input("Er dette korrekt? (1 for Ja, 2 for Nej): \n")
    print("\n\n")
    if add == "1":
        misspelled_words[wrong_word] = correct_word
        print(f"{wrong_word} -> {correct_word} blev tiføjet")

import pickle
with open('misspelled_words_dict.pickle', 'wb') as f:
    # Pickle the 'data' dictionary using the highest protocol available.
    pickle.dump(misspelled_words, f, pickle.HIGHEST_PROTOCOL)

