from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def hello():
    sentence = request.args.get("s", "")
    return f"This is your sentence: {sentence}"