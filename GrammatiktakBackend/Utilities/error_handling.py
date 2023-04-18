## Script for working with errors

class Error():
    def __init__(self, wrong_word: str, right_word: str, indexes: list, description: str) -> None:
        self.wrong_word = wrong_word
        self.right_word = right_word
        self.indexes = indexes
        self.description = description

    def get_description(self):
        return self.description.replace("wrong", self.wrong_word).replace("right", self.right_word)

    def to_list(self):
        return [self.wrong_word, self.right_word, self.indexes, self.get_description()]

