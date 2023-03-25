import re
import os
import requests
from bs4 import BeautifulSoup
import time
from tqdm import tqdm

def get_wikitext():
    url = requests.get("https://da.wikipedia.org/wiki/Special:Random")
    soup = BeautifulSoup(url.content, "html.parser")
    wikitext = ""
    for paragraph in soup.find_all('p'):
        wikitext += paragraph.text
    wikitext = wikitext.replace("Sider for redaktører som er logget ud lær mere", "")
    wikitext = wikitext.replace("\n", "").replace("\t", "")
    wikitext = re.sub(r"\[[0-9]+\]", "", wikitext)
    wikitext = re.sub(r"(?<=\.)(?=[^\s])", " ", wikitext)
    wikitext = wikitext.replace(" [kilde mangler]", "")
    return wikitext

def get_1000_random_wikitext(k=100, n=10):
    os.chdir("GrammatiktakDatasets/uncheckedDatasets/")
    wikitexts = []
    for _ in range(n):
        for _ in tqdm(range(k)):
            wikitexts.append(get_wikitext())
        with open(f"{time.time()}", "w") as f:
            for element in wikitexts:
                f.write(element + "\n")

if "__main__" == __name__:
    get_1000_random_wikitext()
