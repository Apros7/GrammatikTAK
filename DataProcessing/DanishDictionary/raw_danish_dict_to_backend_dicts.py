## When a new updated danish dict has been released this file will create the following files:
# - dictionary_rettet : mistakes in the dictionary (like numbered list) has been removed
# - dictionary_onerow : converted into a unique, one row dictionary
# - genderDict.pickle :
# - verb_ending_dict.pickle
# - sb_ending_dict.pickle
# - SbStemDict.pickle
# - VbStemDict.pickle
# - VbStemToBøjningDict.pickle
# - NutidsrStemDict.pickle
# - NutidsrBøjninger.pickle


# Add feature to capture all words not in dictionary to know if they should be added:

# Words added that is not in dictionary:
# ide, litteraturhistoriker

import os
import pandas as pd
from tqdm import tqdm
import pickle

def load_dictionary():
    os.chdir("/Users/lucasvilsen/Desktop/GrammatikTAK/DataProcessing/DanishDictionary//NewDictHere")
    files = os.listdir(os.getcwd())
    dfs = [pd.read_csv(file, sep=";", header=None, names=["ord1", "ord2", "bøjning"]) for file in files]
    df = pd.concat(dfs)
    os.chdir("/Users/lucasvilsen/Desktop/GrammatikTAK/DataProcessing/DanishDictionary//NewDicts")
    return df

def clean_numbers_from_dictionary(df):
    df["ord1"] = df["ord1"].apply(remove_number)
    df.to_csv("dictionary_rettet.csv", index=False, sep=";")
    return df

def get_one_row(df):
    words1 = df["ord1"].tolist()
    words2 = df["ord2"].tolist()
    one_row = sorted(list(set(words1 + words2)))
    with open("dictionary_onerow.txt", "w") as file:
        for string in one_row: file.write(string + "\n")

def ending_pickles(df):
    verbs, sbs = get_verbs_and_sbs(df)
    verbs_dict, sbs_dict = get_dicts(verbs, sbs)
    with open("verb_ending_dict.pickle", "wb") as f: pickle.dump(verbs_dict, f)
    with open("sb_ending_dict.pickle", "wb") as f: pickle.dump(sbs_dict, f)


def get_verbs_and_sbs(df):
    verbs = []
    sbs = []
    print("Total iterations: ", len(df))
    for i, row in tqdm(df.iterrows()):
        if row["bøjning"] in ["vb.", "ubøj. adj."]: verbs.append((row["ord1"], row["ord2"]))
        elif row["bøjning"] in ["sb.", "sb. pl."]: sbs.append((row["ord1"], row["ord2"]))
    return verbs, sbs

def get_verbs_dict(verbs):
    verbs_dict = {}
    for i in tqdm(range(len(verbs))):
        if verbs[i][1][-4:] == "ende":
            key = verbs[i][1][:-4] + "ene"
            if key in verbs_dict:
                if verbs[i][1] != verbs_dict[key]:
                    print(key, verbs_dict[key], verbs[i][1])
            verbs_dict[key] = verbs[i][1]
    return verbs_dict

def get_sbs_dict(sbs):
    sbs_dict = {}
    for i in tqdm(range(len(sbs))):
        if sbs[i][1][-3:] == "ene":
            key = sbs[i][1][:-3] + "ende"
            if key in sbs_dict:
                if sbs[i][1] != sbs_dict[key]:
                    print(key, sbs_dict[key], sbs[i][1])
            sbs_dict[key] = sbs[i][1]
    return sbs_dict

def get_dicts(verbs, sbs):
    verbs_dict = get_verbs_dict(verbs)
    sbs_dict = get_sbs_dict(sbs)

    new_verbs_dict = {}
    verbs_dict_items = list(verbs_dict.items())
    for i in tqdm(range(len(verbs_dict))):
        if verbs_dict_items[i][1] not in sbs_dict:
            new_verbs_dict[verbs_dict_items[i][0]] = verbs_dict_items[i][1]

    new_sbs_dict = {}
    sbs_dict_items = list(sbs_dict.items())
    for i in tqdm(range(len(sbs_dict))):
        if sbs_dict_items[i][1] not in verbs_dict:
            new_sbs_dict[sbs_dict_items[i][0]] = sbs_dict_items[i][1]
    
    return new_verbs_dict, new_sbs_dict

def get_gender_dict(df):
    # "en" is fællenskøn
    dictionary_is_fælleskøn = {}
    double_words = []

    for i, row in tqdm(df.iterrows()):
        if row['bøjning'] == "sb." and i > 0 and row['ord1'] == row["ord2"]:
            word = df.iloc[i+1]['ord2']
            bool_value = None
            if word[-1] == "n":
                bool_value = True
            elif word[-1] == "t":
                bool_value = False
            second_bool = None
            try: word2 = df.iloc[i+2]['ord2']
            except: continue; 
            if df.iloc[i+2]['ord2'][-1] == "n":
                second_bool = True
            elif df.iloc[i+2]['ord2'][-1] == "t":
                second_bool = False
            if bool_value is not None and second_bool is not None and bool_value != second_bool:
                continue
            if df.iloc[i+1]['ord1'] in dictionary_is_fælleskøn:
                if bool_value is None:
                    continue
                if dictionary_is_fælleskøn[df.iloc[i+1]['ord1']] != bool_value:
                    double_words.append(df.iloc[i+1]['ord1'])
                    continue
            if bool_value is not None:
                dictionary_is_fælleskøn[df.iloc[i+1]['ord1']] = bool_value

    double_words = list(set(double_words))
    for word in double_words: dictionary_is_fælleskøn.pop(word)
    with open("GenderDict.pickle", "wb") as f: pickle.dump(dictionary_is_fælleskøn, f)

def sbs_stem_dict(df):
    sb_dict = {}
    current_lst = []
    for i, row in tqdm(df.iterrows()):
        if row['bøjning'] == "sb." and row['ord1'] == df.iloc[i-1]['ord1']:
            first_word = row['ord1']
            current_lst += [row['ord2']]
            if row['ord1'] not in current_lst:
                current_lst += [row['ord1']]
        elif len(current_lst) > 0:
            for value in list(set(current_lst)):
                sb_dict[value] = first_word
            current_lst = []
            first_word = ""
        elif row['bøjning'] == "sb.":
            first_word = row['ord1']
            current_lst += [row['ord1'], row['ord2']]
    with open("SbStemDict.pickle", "wb") as f: pickle.dump(sb_dict, f)

def count(word1, lst):
    current_count = 0
    for word in lst:
        if word == word1 + "r":
            current_count += 1
    if current_count > 1:
        return True
    return False

def verb_stem_and_nutidsr(df):
    vb_dict = {}
    stem_to_bøjninger = {}
    nutids_r = {}
    nutids_r_stem = {}
    current_lst = []
    lengths = []
    for i, row in tqdm(df.iterrows()):
        if row['bøjning'] == "vb." and row['ord1'] == df.iloc[i-1]['ord1']:
            first_word = row['ord1']
            if row['ord2'] not in current_lst:
                current_lst += [row['ord2']]
            if first_word not in current_lst:
                current_lst += [first_word]
        elif len(current_lst) > 0:
            for value in current_lst:
                vb_dict[value] = first_word
            #print(current_lst[0], current_lst[1], current_lst[0] == current_lst[1])
            if current_lst[0] == current_lst[1]:
                current_lst = current_lst[1:]
            stem_to_bøjninger[first_word] = current_lst
            #print(current_lst)
            lengths.append(len(current_lst))
            infinitiv = current_lst[0]
            nutids_r_word = ""
            for word in current_lst:
                if word == infinitiv + "r":
                    nutids_r_word = word
                    break
            if len(nutids_r_word) > 0:
                nutids_r[first_word] = [infinitiv, nutids_r_word]
                nutids_r_stem[infinitiv] = first_word
                nutids_r_stem[nutids_r_word] = first_word
            current_lst = []
            first_word = ""
        elif row['bøjning'] == "vb.":
            first_word = row['ord1']
            current_lst += [row['ord1'], row['ord2']]

    nutids_r_bøjninger = {}
    nutids_r_stem = {}
    not_correct = []
    for bøjninger in tqdm(stem_to_bøjninger.values()):
        if len(bøjninger) < 4: 
            not_correct.append(bøjninger)
            continue
        infinitiv = bøjninger[0]
        nutids_r = bøjninger[3]
        if nutids_r.replace(infinitiv, "") == "r":
            if count(infinitiv, bøjninger):
                not_correct.append(bøjninger) 
                continue
            nutids_r_bøjninger[infinitiv] = [infinitiv, nutids_r]
            nutids_r_stem[infinitiv] = infinitiv
            nutids_r_stem[nutids_r] = infinitiv
        else: 
            infinitiv = bøjninger[1]
            nutids_r = bøjninger[3]
            if nutids_r.replace(infinitiv, "") == "r":
                if count(infinitiv, bøjninger):
                    not_correct.append(bøjninger) 
                    continue
                nutids_r_bøjninger[infinitiv] = [infinitiv, nutids_r]
                nutids_r_stem[infinitiv] = infinitiv
                nutids_r_stem[nutids_r] = infinitiv
            else:
                infinitiv = bøjninger[0]
                nutids_r = ""
                for word in bøjninger:
                    if word == infinitiv + "r":
                        nutids_r = word
                if len(nutids_r) > 0:
                    nutids_r_bøjninger[infinitiv] = [infinitiv, nutids_r]
                    nutids_r_stem[infinitiv] = infinitiv
                    nutids_r_stem[nutids_r] = infinitiv
                else:
                    infinitiv = bøjninger[0]
                    nutids_r = bøjninger[1]
                    if infinitiv.replace(nutids_r, "") == "e":
                        nutids_r_bøjninger[infinitiv] = [infinitiv, nutids_r]
                        nutids_r_stem[infinitiv] = infinitiv
                        nutids_r_stem[nutids_r] = infinitiv
                    else:
                        infinitiv = bøjninger[1]
                        nutids_r = ""
                        for word in bøjninger:
                            if word == infinitiv + "r":
                                nutids_r = word
                        if len(nutids_r) > 0:
                            nutids_r_bøjninger[infinitiv] = [infinitiv, nutids_r]
                            nutids_r_stem[infinitiv] = infinitiv
                            nutids_r_stem[nutids_r] = infinitiv
                        else:
                            not_correct.append(bøjninger)  

    with open("VbStemDict.pickle", "wb") as f: pickle.dump(vb_dict, f)
    with open("VbStemToBøjningDict.pickle", "wb") as f: pickle.dump(stem_to_bøjninger, f)
    with open("nutids_r_bøjninger.pickle", "wb") as f: pickle.dump(nutids_r_bøjninger, f)
    with open("nutids_r_stem.pickle", "wb") as f: pickle.dump(nutids_r_stem, f)

def remove_number(value):
    if value[0].isdigit(): return value[3:]
    else: return value

def main():
    raw_df = load_dictionary()
    df = clean_numbers_from_dictionary(raw_df)
    get_one_row(df)
    ending_pickles(df)
    get_gender_dict(df)
    sbs_stem_dict(df)
    verb_stem_and_nutidsr(df)

main()
