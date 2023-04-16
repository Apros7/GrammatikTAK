
# initailize the tracker
from Timetracking.timetracker import TimeTracker
time_tracker = TimeTracker()
time_tracker.inactive = True

# import internal modules for correcting
from Punctuation.correct_punctuation import PunctuationCorrector
from Helpers.tagger import Tagger
from Spellchecking.capitalized import CapitalizationCorrector
#from Spellchecking.nutids_r import NutidsRCorrector
from Spellchecking.determinant import determinantCorrector
from Utilities.utils import concat_errors, check_empty_input_or_feedback, check_if_index_is_correct, sort_errors

# import external modules for storage
from Storage.Firestore import FirestoreClient

# importing external modules
from flask import Flask, request, jsonify
from flask_cors import CORS

time_tracker.track("import modules")

# initialize correctors:
punctuation_corrector = PunctuationCorrector()
capitalize_corrector = CapitalizationCorrector()
tagger = Tagger()
determinant_corrector = determinantCorrector()
#nutids_corrector = NutidsRCorrector()

# initialize firestore client:
firestore_client = FirestoreClient()

time_tracker.track("initialize correctors")

# corrector function

def correct_input(input, save=False):
    punctuation_errors = punctuation_corrector.correct_punctuation(input)
    time_tracker.track("correct punctuation")

    pos_tags, ner_tags = tagger.get_tags(input)
    time_tracker.track("get tags")

    determinant_errors = determinant_corrector.correct_determinants(input, pos_tags)
    time_tracker.track("correct determinant")

    capitalization_errors = capitalize_corrector.correct_capitalization(input, pos_tags, ner_tags)
    time_tracker.track("correct capitalization")

    # nutids_errors = nutids_corrector.correct(input, pos_tags)
    # print("NUTIDS ERRORS:\n")
    # print(nutids_errors)
    # time_tracker.track("nutids r")

    if save:
        firestore_client.save_input(input)
        time_tracker.track("saving to firestore")
    return sort_errors(concat_errors(punctuation_errors + capitalization_errors + determinant_errors))

# flask app:
app = Flask(__name__)
CORS(app)
@app.route("/", methods=["POST"])

def index():
    data = request.get_json()
    empty_or_feedback, feedback, input, output = check_empty_input_or_feedback(data)
    if empty_or_feedback:
        firestore_client.save_feedback(feedback, input)
        return jsonify(output)
    input = data["sentence"]
    output = correct_input(input, save=True)
    return jsonify(output)

time_tracker.complete_reset()

#message = "Hej jeg hedder lucas. Jeg havde engang en hund. Den har jeg ikke mere. Den er nu i Silkeborg. Jeg går på Silkeborg Gymnasium."
#message = "Jeg kan ikke lærer og cyklede det hele på en dag. Jeg lære dansk i skolen"
#message = "Jeg har et rigtig rigtig hurtig ven"
#message = "Jeg bor i det hus, som den anden pige allerede har boet i."
message = "Min and spiser massere af rødbedesaft og den løber popcorn."
#message = "Dertil er der også dobbeltblinding hvor hverken patienten eller personalet ved om den behandling de får/giver er den faktiske behandling eller blot placebo. Jeg ved godt at jeg burde vide det."
#message = "Rigtig mange glæde sig til at ser og inviterer familie og venner."
#message = "hey Christian<br>tak for Det. Jeg er desværre I skole til, kl 18, så det har Lucas ikke mulighed for.<br>Jeg håber, at i får en dejlig aften :smile:."
#message = "En anden form for bias er confirmation bias, hvor man som forsker vægte undersøgelser som understøtte ens hypotse end undersøgelser som vil modsige ens hypotese. Det omfatter også, at hvis man har en vis forventning af et bestemt præparat virkning, at man i så fald også vil fortolke ens data på en måde som understøtter ens forventning. Confirmation bias kan også påvirke ens testpersoner, hvis man ikke er opmærksom på dette. Fx hvis man giver en testperson et præparat som testpersonen forventer har en effekt, vil dette kunne påvirke testpersonens opfattelse af stoffets virkning, på en måde som igen understøtter ens forventning. I det sidstnævnte eksempel er det placeboeffekten som vil kunne give patienten en fornemmelse af at præparatet virker selvom det ikke nødvendigvis er tilfældet. For at modvirker confirmation bias kan man foretage sig af blinding i tre forskellige grader. Ved almindelig blinding ved selve deltagerne i studiet ikke om de modtager den aktuelle behandling eller om de ikke gør, fx ved at give en kalkpille eller lign. Dette er med til at modvirke patientens egne forventninger til behandlingen. Dertil er der også dobbeltblinding hvor hverken patienten eller personalet ved om den behandling de får/giver er den faktiske behandling eller blot placebo. Dette er med til at modvirke at personalets forventning til behandlingen videregives ubevidst under kommunikation. Til sidst kan man også tripelblinde, der lægges til de to tidligere med at dem som behandlinger og analyser data fra studiet ikke ved hvilken gruppe som har modtaget den faktiske behandling. Disse tre former for blinding bidrager til at mindske mængden af confirmation bias mest muligt."
# errors1 = correct_input(message)
# print(*errors1, sep="\n")
# check_if_index_is_correct(errors1, message)

time_tracker.track2("end")
time_tracker(.5)

