import requests
from bs4 import BeautifulSoup
import webbrowser

url = requests.get("https://da.wikipedia.org/wiki/Special:Random")
soup = BeautifulSoup(url.content, "html.parser")
wikitext = ""
for paragraph in soup.find_all('p'):
    wikitext += paragraph.text
