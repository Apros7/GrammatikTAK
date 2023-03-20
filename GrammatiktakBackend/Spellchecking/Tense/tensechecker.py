
# Script to include all the tense correctors in a single class:
from Spellchecking.Tense.nutids_r import NutidsRCorrector

class TenseCorrector():
    def __init__(self) -> None:
        self.nutids_r_corrector = NutidsRCorrector()

    def correct_tense(self, sentence, pos):
        nutids_r_errors = self.nutids_r_corrector.correct_nutids_r(sentence, pos)
        return nutids_r_errors