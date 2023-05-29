from flask import Flask, request, redirect, flash
import time
import pandas as pd
import os
from GrammatiktakTestDatasets.getDatasets.get_wiki_text import get_wikitext

app = Flask(__name__)
app.secret_key = 'jegharensupersværkodeatgætte123'
start_time = time.time()
prev_text = None

text = []

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
                <input type="submit" value="Submit">
            </form>
            <form method="POST" action="/skip" id="skip-form"> <input type="submit" value="Skip"> </form>
            <form method="POST" action="/go-back" id="go-back-form"> <input type="submit" value="Back"> </form>
        </div>
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
