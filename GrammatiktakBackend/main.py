from Timetracking.timetracker import TimeTracker
time_tracker = TimeTracker()
time_tracker.inactive = True

from Punctuation.correct_punctuation import PunctuationCorrector
from Helpers.tagger import Tagger
from Spellchecking.capitalized import CapitalizationCorrector
from Spellchecking.nutids_r import NutidsRCorrector
from Spellchecking.determinant import DeterminantCorrector
from Spellchecking.spelling_errors import SpellChecker
from SentenceStructure.missing_foundation import MissingFoundationChecker
from SentenceStructure.double_words import DoubleWordsChecker
from Punctuation.excessive_spaces import ExcessiveSpacesCorrector

from Utilities import utils
from Utilities.error_handling import error_concatenator
from Utilities.module_utils import ModuleSequential, ModuleSequentialWhenSentenceManipulation, ModuleTracker
from Utilities.deployment_test import test_deployment

from Storage.Firestore import FirestoreClient

from flask import Flask, request, jsonify
from flask_cors import CORS

time_tracker.track("import modules")

module_tracker = ModuleTracker()
tagger = Tagger()

modules_to_manipulate_sentence = ModuleSequentialWhenSentenceManipulation([
    MissingFoundationChecker(),
    NutidsRCorrector()
], timeTracker=time_tracker, moduleTracker = module_tracker)

modules_to_manipulate_and_project = ModuleSequentialWhenSentenceManipulation([
    ExcessiveSpacesCorrector(),
    DoubleWordsChecker()
], timeTracker=time_tracker, moduleTracker = module_tracker)

modules_to_project_onto_others = ModuleSequential([
    PunctuationCorrector(),
    CapitalizationCorrector()
], timeTracker=time_tracker, moduleTracker = module_tracker)

modules_be_projected_on = ModuleSequential([
    DeterminantCorrector(),
    SpellChecker()
], timeTracker=time_tracker, moduleTracker = module_tracker)

firestore_client = FirestoreClient()

time_tracker.track("initialize correctors")

def correct_input(input_sentence, save=False):
    index_finder = utils.IndexFinder(original_sentence=input_sentence) # Should reset every time, therefore here

    # In case of backend error, the input sentence will show on Google Cloud Logs
    print("Correcting this sentence: ", input_sentence)

    pos_tags, ner_tags = tagger.get_tags(input_sentence)
    time_tracker.track("get tags")

    sentence_manipulation_project_errors, (sentence, pos_tags, ner_tags) = modules_to_manipulate_and_project.correct(input_sentence, pos_tags, ner_tags, index_finder=index_finder)

    sentence_manipulation_errors, (sentence, pos_tags, ner_tags) = modules_to_manipulate_sentence.correct(sentence, pos_tags, ner_tags, index_finder=index_finder)

    errors_be_projected_on = modules_be_projected_on.correct(sentence, pos_tags, ner_tags, index_finder=index_finder)

    errors_to_project_onto_others = modules_to_project_onto_others.correct(sentence, pos_tags, ner_tags, index_finder=index_finder)

    # utils.print_list_of_ErrorList(sentence_manipulation_project_errors, sentence_manipulation_errors, errors_be_projected_on, errors_to_project_onto_others)

    if save:
        firestore_client.save_input(sentence)
        time_tracker.track("saving to firestore")

    final_errors = error_concatenator(errors_be_projected_on + sentence_manipulation_errors, 
                                      errors_to_project_onto_others=sentence_manipulation_project_errors + errors_to_project_onto_others)

    return final_errors

# flask app:
app = Flask(__name__)
CORS(app)
@app.route("/", methods=["POST"])

def index():
    data = request.get_json()
    empty_or_feedback, feedback, input, output = utils.check_empty_input_or_feedback(data)
    if empty_or_feedback:
        firestore_client.save_feedback(feedback, input)
        return jsonify(output)
    input = data["sentence"]
    output = correct_input(input, save=True)
    return jsonify(output)

time_tracker.complete_reset()

message = "jeg hedder magnus og min ven hedder lucas hvilket jeg er glad for"
errors1 = correct_input(message)
print(*errors1, sep="\n")
utils.check_if_index_is_correct(errors1, message)
module_tracker.print()

# test_deployment(correct_input, manual_check=False, start_at=0, time_tracker=time_tracker)

## NOTES ##
# Spellchecker virker ikke helt godt stadigvæk (burde testes ved rigtige ord, som ikke er i ordbogen) (2)

time_tracker.track2("end")
time_tracker(.5)

