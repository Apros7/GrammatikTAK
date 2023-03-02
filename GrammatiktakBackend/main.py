# initailize the tracker
from Timetracking.timetracker import TimeTracker
time_tracker = TimeTracker()
# time_tracker.inactive = True

# import internal modules
from Punctuation.correct_punctuation import PunctuationCorrector
from Spellchecking.tagger import Tagger
from Spellchecking.capitalized import CapitalizationCorrector
from Utilities.utils import prepare_sentence

# importing external modules
# from polyleven import levenshtein
from flask import Flask, request, jsonify
from flask_cors import CORS

time_tracker.track("import modules")

# initialize correctors:
punctuation_corrector = PunctuationCorrector()
capitalize_corrector = CapitalizationCorrector()
tagger = Tagger()

time_tracker.track("initialize correctors")

def correct_input(input):
    punctuation_errors = punctuation_corrector.correct_punctuation(input)
    time_tracker.track("correct punctuation")
    pos_tags, ner_tags = tagger.get_tags(input)
    time_tracker.track("get tags")
    return punctuation_errors, pos_tags, ner_tags

app = Flask(__name__)
CORS(app)
@app.route("/", methods=["POST"])

def index():
    global all_errors, errors, new_lines
    all_errors, errors, new_lines = [], [], []
    data = request.get_json()
    input = data["sentence"]
    output = correct_input(input)
    #print(*output, sep="\n")
    return jsonify(output)

time_tracker.complete_reset()

message = "Hey Christian.<br>Tak for det. Jeg er desværre i skole til kl 18, så det har jeg ikke mulighed for.<br>Jeg håber, at I får en dejlig aften :smile:."
#message = "En anden form for bias er confirmation bias, hvor man som forsker vægte undersøgelser som understøtte ens hypotse end undersøgelser som vil modsige ens hypotese. Det omfatter også, at hvis man har en vis forventning af et bestemt præparat virkning, at man i så fald også vil fortolke ens data på en måde som understøtter ens forventning. Confirmation bias kan også påvirke ens testpersoner, hvis man ikke er opmærksom på dette. Fx hvis man giver en testperson et præparat som testpersonen forventer har en effekt, vil dette kunne påvirke testpersonens opfattelse af stoffets virkning, på en måde som igen understøtter ens forventning. I det sidstnævnte eksempel er det placeboeffekten som vil kunne give patienten en fornemmelse af at præparatet virker selvom det ikke nødvendigvis er tilfældet. For at modvirker confirmation bias kan man foretage sig af blinding i tre forskellige grader. Ved almindelig blinding ved selve deltagerne i studiet ikke om de modtager den aktuelle behandling eller om de ikke gør, fx ved at give en kalkpille eller lign. Dette er med til at modvirke patientens egne forventninger til behandlingen. Dertil er der også dobbeltblinding hvor hverken patienten eller personalet ved om den behandling de får/giver er den faktiske behandling eller blot placebo. Dette er med til at modvirke at personalets forventning til behandlingen videregives ubevidst under kommunikation. Til sidst kan man også tripelblinde, der lægges til de to tidligere med at dem som behandlinger og analyser data fra studiet ikke ved hvilken gruppe som har modtaget den faktiske behandling. Disse tre former for blinding bidrager til at mindske mængden af confirmation bias mest muligt."
prepared = " ".join(prepare_sentence(message))
print(correct_input(message)[0])

time_tracker.track2("end")
time_tracker(.5)

