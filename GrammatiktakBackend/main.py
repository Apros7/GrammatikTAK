from Timetracking.timetracker import TimeTracker
time_tracker = TimeTracker()
# time_tracker.inactive = True

from Punctuation.correct_punctuation import PunctuationCorrector
from Helpers.tagger import Tagger
from Spellchecking.capitalized import CapitalizationCorrector
from Spellchecking.nutids_r import NutidsRCorrector
from Spellchecking.determinant import DeterminantCorrector
from Spellchecking.spelling_errors import SpellChecker
from SentenceStructure.missing_foundation import MissingFoundationChecker

from Utilities.utils import check_empty_input_or_feedback, check_if_index_is_correct, prepare_sentence, IndexFinder
from Utilities.error_handling import error_concatenator
from Utilities.module_utils import ModuleSequential
from Utilities.deployment_test import test_deployment

from Storage.Firestore import FirestoreClient

from flask import Flask, request, jsonify
from flask_cors import CORS

time_tracker.track("import modules")

tagger = Tagger()

modules_pre_foundation = ModuleSequential([
    CapitalizationCorrector()
], timeTracker=time_tracker)

modules_to_project_onto_others = ModuleSequential([
    PunctuationCorrector()
], timeTracker=time_tracker)

modules_be_projected_on = ModuleSequential([
    DeterminantCorrector(),
    NutidsRCorrector(),
    SpellChecker()
], timeTracker=time_tracker)

# Modules that change sentence, pos or ner are idenpentially initialized and used
missing_foundation_checker = MissingFoundationChecker()

firestore_client = FirestoreClient()

time_tracker.track("initialize correctors")

def correct_input(input_sentence, save=False):
    index_finder = IndexFinder()

    pos_tags, ner_tags = tagger.get_tags(input_sentence)
    time_tracker.track("get tags")

    errors_pre_foundation = modules_pre_foundation.correct(input_sentence, pos_tags, ner_tags, index_finder = IndexFinder(), ignore_indexes = True)

    index_finder.ignore_indexes = True
    foundation_errors, (sentence, pos_tags, ner_tags), index_finder = missing_foundation_checker.correct(input_sentence, pos_tags, ner_tags, index_finder)
    # print("FOUNDATION ERRORS: ")
    # print(*foundation_errors.to_list(finalize=True), sep="\n")
    time_tracker.track("module FoundationChecker")

    errors_be_projected_on = modules_be_projected_on.correct(sentence, pos_tags, ner_tags, index_finder=index_finder)
    errors_to_project_onto_others = modules_to_project_onto_others.correct(sentence, pos_tags, ner_tags, index_finder=index_finder)

    if save:
        firestore_client.save_input(sentence)
        time_tracker.track("saving to firestore")

    final_errors = error_concatenator(errors_be_projected_on + [foundation_errors], 
                                      errors_to_project_onto_others=errors_to_project_onto_others + errors_pre_foundation)

    return final_errors

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

# message = "Hej jeg hedder lucas. Jeg havde engang en hund. Den har jeg ikke mere. Den er nu i Silkeborg. Jeg går på Silkeborg Gymnasium."
# message = "Jeg kan ikke lærer og cyklede det hele på en dag. Jeg lære dansk i skolen"
# message = "Jeg har et rigtig rigtig hurtig ven"
# message = "Jeg bor i det hus, som den anden pige allerede har boet i."
# message = "min and spiser massere af rødbedesaft og den løbe popcorn"
# message = "Det er som om, at vinterens mørke og kulde forlader mig med et dybt suk."
# message = "Jeg kigger op og ser solens første svage stråler, som titter frem mellem bøgetræerne og varmer den kolde jord. De første spæde og grønne blade pynter på bøgetræernes ellers nøgne grene. Skoven er som et eventyr, hvor fuglene synger med på forårets melodi. Solens stråler varmer mine kinder, og jeg mærker, hvordan lyset og den positive energi gennemstrømmer min krop. Det er som om, at vinterens mørke og kulde forlader mig med et dybt suk. Mine tanker ledes hen på naturens store betydning for ikke blot mig, men for mange mennesker her på jorden. Specielt i digte kan man finde mange afskygninger af naturens rolle i livet hos mennesker. Der findes netop mange digtere, som i tidens løb har skrevet og reflekteret over naturen. Nogen kan spejle sig eller finde en del af sig selv i naturen. Andre finder måske en ensomhed i naturens store pragt. Det får mig til at undres, for hvorfor opstilles naturen som motiv i mange digte? Hvilken betydning har naturen for mennesket, og hvordan kommer dette til udtryk i digte?"
# message = """cHer bruges billedsprog til at sammenligne det lyriske jeg med træerne. Det lyriske jeg spejler sig altså i træerne, idet han forestiller sig sine hænder som grene. Forestillingen om, at træerne næsten ikke kan nå hinanden med deres grene, kan altså overføres på det lyriske jeg. Måske har det lyriske jeg selv svært ved at nå nogen. Måske føler det lyriske jeg, at han ikke kan nå kærligheden. Måske føler det lyriske jeg, at han glider væk fra en elsket. Netop denne ide, hvor naturen bruges som en analogi til mennesket selv, fremsættes i den danske litteraturhistoriker Erik Skyum-Nielsens artikel ”Nu er det tid til naturdigte”. Her forklarer han, at ”så snart en digter beskrev og besang naturen, kom digtet også altid til at handle om digteren selv. I den forstand fungerer naturen uundgåeligt som menneskets spejl.” Netop pga. Erik Skyum-Nielsens baggrund som lektor på institut for Nordiske Studier og Sprogvidenskab på Københavns Universitet kan denne betragtning ses som troværdig. Naturen i digte er altså en måde, hvorpå digteren indirekte kan reflektere og skrive om sig selv."""
# message = "Dertil er der også dobbeltblinding hvor hverken patienten eller personalet ved om den behandling de får/giver er den faktiske behandling eller blot placebo. Jeg ved godt at jeg burde vide det."
# message = "den hus er rigtig stor. Rigtig mange glæde sig til at ser og inviterer familie og venner."
# message = "hey Christian<br>tak for Det. Jeg er desværre I skole til, kl 18, så det har Lucas ikke mulighed for.<br>Jeg håber, at i får en dejlig aften :smile:."
# message = "En anden form for bias er confirmation bias, hvor man som forsker vægte undersøgelser som understøtte ens hypotse end undersøgelser som vil modsige ens hypotese. Det omfatter også, at hvis man har en vis forventning af et bestemt præparat virkning, at man i så fald også vil fortolke ens data på en måde som understøtter ens forventning. Confirmation bias kan også påvirke ens testpersoner, hvis man ikke er opmærksom på dette. Fx hvis man giver en testperson et præparat som testpersonen forventer har en effekt, vil dette kunne påvirke testpersonens opfattelse af stoffets virkning, på en måde som igen understøtter ens forventning. I det sidstnævnte eksempel er det placeboeffekten som vil kunne give patienten en fornemmelse af at præparatet virker selvom det ikke nødvendigvis er tilfældet. For at modvirker confirmation bias kan man foretage sig af blinding i tre forskellige grader. Ved almindelig blinding ved selve deltagerne i studiet ikke om de modtager den aktuelle behandling eller om de ikke gør, fx ved at give en kalkpille eller lign. Dette er med til at modvirke patientens egne forventninger til behandlingen. Dertil er der også dobbeltblinding hvor hverken patienten eller personalet ved om den behandling de får/giver er den faktiske behandling eller blot placebo. Dette er med til at modvirke at personalets forventning til behandlingen videregives ubevidst under kommunikation. Til sidst kan man også tripelblinde, der lægges til de to tidligere med at dem som behandlinger og analyser data fra studiet ikke ved hvilken gruppe som har modtaget den faktiske behandling. Disse tre former for blinding bidrager til at mindske mængden af confirmation bias mest muligt."
# message = "En anden form for bias er confirmation bias, hvor man som forsker vægte undersøgelser som understøtte ens hypotse end undersøgelser som vil modsige ens hypotese. Det omfatter også, at hvis man har en vis forventning af et bestemt præparat virkning, at man i så fald også vil fortolke ens data på en måde som understøtter ens forventning."
# message = "Hey. Jeg håber, at du nyder weekenden :smile:. Jeg har endelig fået lavet et fix til edit detection til web-anno. Jeg har lavet en PR med det. Hvis du vil approve og restarte serveren, så skal jeg nok nå så mange reviews, som jeg kan i løbet af i dag og i morgen."
# message = "Jeg skal på arbejde d. 9. august 2022."
# message = "hej jeg hedder lucas. hej jeg hedder lucas"
# message = "Super sejt, Simon Gaarde💪💪💪. Vi ved du kæmper til tårerne triller og hvor meget du giver afkald på, for at nå dine mål i vandet - du skal være SÅ stolt🇩🇰🇩🇰🇩🇰. Jeg kan godt lide danske gulerødder 💪💪🚀"
# message = "Super sejt, Simon Gaarde. Vi ved du kæmper til tårerne triller og hvor meget du giver afkald på, for at nå dine mål i vandet - du skal være SÅ, stolt."
# message = "Træner teamet Mathilde Pugholm Hvid, Nichlas Fonnesbech & Bastian Løve Høegh - Jeg tror ikke helt I ved, hvor KÆMPE en forskel I gør - TUSIND TAK🙏🙏."
# message = "jeg heder lucas. jeg har fødseldag idag"
# message = "Jeg håber ikke, at du skulle vente så lang tid på, at den blev færdig."
# message = "Så er vi tilbage på 0 på annotate. Jeg har sendt billeder af statistics. Jeg har også lavet en PE med nogle fixes, flere static filtre og evnen til at specificere om en person faller på videoen, sover og hvorvidt patienten har dyne på. Jeg kan vise mere i morgen. Er du på kontoret i morgen?"
# message = "9 mennesker boede på en gammel ø.. De havde en god ven"
# message = "idag har jeg fødseldag. Jeg har fødselsdag idag"
# message = "jeg har en stor hus. Jeg har et stor hus. Jeg har en stort hund"
# message = "jeg har en met til skole"

message = "Håber du har en god dag. Har du en god dag? Har en god dag. Har du haft en god dag? Har du spist en banan? Håber du hygger."
errors1 = correct_input(message)
print(*errors1, sep="\n")
check_if_index_is_correct(errors1, message)

time_tracker.track2("end")
time_tracker(.5)

