"""
Function in google cloud should be:
def index():
    sentence = request.form["sentence"]
    if sentence is None or sentence == "":
        return jsonify("error: no sentence")
    data = complete_correction(sentence)
    return jsonify(data)
"""

#service_url = "https://backend1-2f53ohkurq-ey.a.run.app/"

import requests

sentence = "hej jeg hedder per"
object = {"sentence": sentence}
service_url = "http://127.0.0.1:5000/"
resp = requests.post(service_url, data=object)

print(resp.text)