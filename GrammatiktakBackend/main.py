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
from SentenceStructure.double_words import DoubleWordsChecker

from Utilities.utils import check_empty_input_or_feedback, check_if_index_is_correct, IndexFinder
from Utilities.error_handling import error_concatenator
from Utilities.module_utils import ModuleSequential, ModuleSequentialWhenSentenceManipulation
from Utilities.deployment_test import test_deployment

from Storage.Firestore import FirestoreClient

from flask import Flask, request, jsonify
from flask_cors import CORS

time_tracker.track("import modules")

tagger = Tagger()

modules_to_manipulate_sentence = ModuleSequentialWhenSentenceManipulation([
    MissingFoundationChecker(),
    DoubleWordsChecker()
], timeTracker=time_tracker)

modules_to_project_onto_others = ModuleSequential([
    PunctuationCorrector(),
    CapitalizationCorrector()
], timeTracker=time_tracker)

modules_be_projected_on = ModuleSequential([
    DeterminantCorrector(),
    NutidsRCorrector(),
    SpellChecker()
], timeTracker=time_tracker)

firestore_client = FirestoreClient()

time_tracker.track("initialize correctors")

def correct_input(input_sentence, save=False):
    index_finder = IndexFinder(original_sentence=input_sentence) # Should reset every time, therefore here

    pos_tags, ner_tags = tagger.get_tags(input_sentence)
    time_tracker.track("get tags")

    sentence_manipulation_errors, (sentence, pos_tags, ner_tags) = modules_to_manipulate_sentence.correct(input_sentence, pos_tags, ner_tags, index_finder=index_finder)
    errors_be_projected_on = modules_be_projected_on.correct(sentence, pos_tags, ner_tags, index_finder=index_finder)
    errors_to_project_onto_others = modules_to_project_onto_others.correct(sentence, pos_tags, ner_tags, index_finder=index_finder)

    if save:
        firestore_client.save_input(sentence)
        time_tracker.track("saving to firestore")

    final_errors = error_concatenator(errors_be_projected_on + sentence_manipulation_errors, 
                                      errors_to_project_onto_others=errors_to_project_onto_others)

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

message = "håber du har en god dag på silkeborg gymnasie. Har du en god dag? Har en god dag. Har du haft en god dag? Har du spist en banan? Håber du hygger."
message = "jeg kører 30 km/t"
message = "jeg jeg ser en action film fra fra blockbuster. Så så jeg en film. Lars Lars har det godt. Jeg er fra fra fra silkeborg. Jeg har skole imorgen. Jeg er er er er er"
message = "håber du har en god dag på silkeborg gymnasium."
message = "håber du har en god dag på silkeborg silkeborg gymnasium"
message = "Hvordan har du det? Det går godt her."
message = "jeg jeg har har et et sødt sødt hund hund"
message = "jeg jeg har en stor hus. jeg går på silkeborg silkeborg gymnasium. Jeg har et stor hus. Jeg har en stort hund."
message = "jeg jeg ser en action film fra fra blockbuster. Så så jeg en film. Lars Lars har det godt. Jeg er fra fra fra silkeborg. Jeg har skole imorgen. Jeg er er er er er"

errors1 = correct_input(message)
# print(*errors1, sep="\n")
# check_if_index_is_correct(errors1, message)
test_deployment(correct_input)

time_tracker.track2("end")
time_tracker(.5)

