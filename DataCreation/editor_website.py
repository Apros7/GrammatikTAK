from flask import Flask, request, redirect, flash
import requests
from bs4 import BeautifulSoup
import time

app = Flask(__name__)

text = ""

def get_wikitext():
    url = requests.get("https://da.wikipedia.org/wiki/Special:Random")
    soup = BeautifulSoup(url.content, "html.parser")
    wikitext = ""
    for paragraph in soup.find_all('p'):
        wikitext += paragraph.text
    return wikitext

@app.route('/')
def index():
    wikitext = get_wikitext()
    return f'''
        <div style="text-align:center">
            <form method="POST" action="/submit">
                <textarea name="editor" style="width:50%;margin:auto;height:600px">{wikitext}</textarea>
                <br>
                <input type="submit" value="Submit">
            </form>
        </div>
    '''

@app.route('/submit', methods=['POST'])
def submit():
    global text
    flash('Text successfully added!')
    time.sleep(1)
    text += request.form['editor']
    return redirect("/")

if __name__ == '__main__':
    app.run()
