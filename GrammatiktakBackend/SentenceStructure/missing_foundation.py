
from Utilities.utils import prepare_sentence, move_index_based_on_br, find_index, get_pos_without_information

def MissingFoundationChecker():
    """
    Based on logic
    Hvis VERB - PRON - VERB, så mangler PRON først.
    """
    def __init__():
        pass

    def create_error_message():
        pass

    def correct(self, sentence, pos_tags, ner_tags):
        words = prepare_sentence(sentence)
        pos = get_pos_without_information(pos_tags)
        return None