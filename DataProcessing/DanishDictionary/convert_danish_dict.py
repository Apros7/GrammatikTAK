import pandas as pd

df = pd.read_csv("Datasets/ordlisteFuldform2021rettet.csv")
unique1 = df["ord1"].unique()
unique2 = df["ord2"].unique()
print(len(unique1), len(unique2))
print(len(set(unique1)), len(set(unique2)))
unique = set(unique1).union(set(unique2))
print(len(unique))

with open("Datasets/ordlisteFuldform2021OneRow.csv", "w") as f: 
    f.write("ord\n")
    for val in unique:
        f.write(f"{val}\n")