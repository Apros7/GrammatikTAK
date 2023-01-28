from flask import Flask, request, redirect, flash
import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import re
import os

app = Flask(__name__)
app.secret_key = 'jegharensupersværkodeatgætte123'
start_time = time.time()
prev_text = None

text = []

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

def update_progress(text):
    df = pd.DataFrame(text)
    df.to_csv('../DataCreationDatasets/Dataset_' + str(start_time), header=None, index=False)


@app.route('/')
def index():
    global prev_text
    wikitext = get_wikitext() if prev_text is None else prev_text
    prev_text = None
    return (f'''
        <div style="text-align:center">
            <form method="POST" action="/submit" id="submit-form">
                <textarea name="editor" style="width:50%;margin:auto;height:600px">{wikitext}</textarea>
                <br>
                <input type="submit" value="Submit [A]">
            </form>
            <form method="POST" action="/skip" id="skip-form"> <input type="submit" value="Skip [S]"> </form>
            <form method="POST" action="/go-back" id="go-back-form"> <input type="submit" value="Back [B]"> </form>
        </div>
    ''' +
    '''
        <script>
        document.addEventListener("keydown", function(event) {
            if (event.code === "KeyA") {
            document.getElementById("submit-form").submit();
            } else if (event.code === "KeyS") {
            document.getElementById("skip-form").submit();
            } else if (event.code === "KeyB") {
            document.getElementById("go-back-form").submit();
            }
        });
        </script>
    ''')

@app.route('/submit', methods=['POST'])
def submit():
    global text
    text.append(str(request.form['editor']))
    update_progress(text)
    print(request.form['editor'])
    return redirect("/")

@app.route('/skip', methods=['POST'])
def skip():
    return redirect("/")

@app.route('/go-back', methods=['POST'])
def go_back():
    global text, prev_text
    prev_text = text[-1]
    text = text[:-1]
    update_progress(text)
    return redirect("/")

if __name__ == '__main__':
    app.run()
