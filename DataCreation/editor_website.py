from flask import Flask, request, redirect, flash
import requests
from bs4 import BeautifulSoup
import time

app = Flask(__name__)
app.secret_key = 'jegharensupersværkodeatgætte123'
start_time = time.time()

text = ""

def get_wikitext():
    url = requests.get("https://da.wikipedia.org/wiki/Special:Random")
    soup = BeautifulSoup(url.content, "html.parser")
    wikitext = ""
    for paragraph in soup.find_all('p'):
        wikitext += paragraph.text
    wikitext = wikitext.replace("Sider for redaktører som er logget ud lær mere", "")
    wikitext = wikitext.replace("\n", "").replace("\t", "")
    print(wikitext)
    return wikitext

def update_progress(text):
    with open('document.csv','a') as fd:
        fd.write(text)


@app.route('/')
def index():
    wikitext = get_wikitext()
    return (f'''
        <div style="text-align:center">
            <form method="POST" action="/submit" id="submit-form">
                <textarea name="editor" style="width:50%;margin:auto;height:600px">{wikitext}</textarea>
                <br>
                <input type="submit" value="Submit">
            </form>
            <form method="POST" action="/skip" id="skip-form"> <input type="submit" value="Skip"> </form>
        </div>
    ''' +
    '''
        <script>
        document.addEventListener("keydown", function(event) {
            if (event.code === "KeyA") {
            document.getElementById("submit-form").submit();
            } else if (event.code === "KeyS") {
            document.getElementById("skip-form").submit();
            }
        });
        </script>
    ''')

@app.route('/submit', methods=['POST'])
def submit():
    global text
    time.sleep(0.2)
    text += request.form['editor']
    update_progress(request.form['editor'])
    print(request.form['editor'])
    return redirect("/")

@app.route('/skip', methods=['POST'])
def skip():
    return redirect("/")

if __name__ == '__main__':
    app.run()
