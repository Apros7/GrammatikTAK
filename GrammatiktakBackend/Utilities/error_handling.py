## Script for working with errors

class Error():
    def __init__(self, wrong_word: str = None, right_word: str = None, indexes: list = None, description: str = None) -> None:
        self.wrong_word = wrong_word
        self.right_word = right_word
        self.indexes = indexes
        self.description = description

    def get_description(self):
        return self.description.replace("wrong", self.wrong_word).replace("right", self.right_word)

    def is_healthy(self):
        if len([var_name for var_name, var_value in self.__dict__.items() if var_value is None]) == 0:
            return True
        return False

    def to_list(self):
        if self.is_healthy():
            return [self.wrong_word, self.right_word, self.indexes, self.get_description()]
        missing_instance_variables = [var_name for var_name, var_value in self.__dict__.items() if var_value is None]
        raise NotImplementedError(f"Error is not healthy. Please fill these variables: {[missing_instance_variables]}")

