from collections import defaultdict

approved_types = ["add_punc", "del_punc", "det", "add_cap", "del_cap", "nutids-r", "spellcheck", "foundation"]
error_types_to_concat = ["add_punc", "del_punc", "add_cap", "del_cap"]

def init_dict():
    def def_value():
        return []
    return defaultdict(def_value)

def errors_to_index_dict(errors):
    dict = init_dict()
    if not isinstance(errors, list):
        errors = list(errors)
    for errorList in errors:
        for error in errorList.errors:
            dict[tuple(error.indexes)].append(error)
    return dict

def add_punc(error, error2):
    wrong_word = error.wrong_word
    right_word = error.right_word + error2.right_word[-1]
    indexes = error.indexes
    description = error.description + " " + error2.description
    return Error(wrong_word, right_word, indexes, description, error.get_type())

def del_punc(error, error2):
    wrong_word = error.wrong_word
    right_word = error.right_word[:-1]
    indexes = error.indexes
    description = error.description + " " + error2.description
    return Error(wrong_word, right_word, indexes, description, error.get_type())

def add_cap(error, error2):
    wrong_word = error.wrong_word
    right_word = error.right_word.capitalize()
    indexes = error.indexes
    description = error.description + " " + error2.description
    return Error(wrong_word, right_word, indexes, description, error.get_type())

def del_cap(error, error2):
    wrong_word = error.wrong_word
    right_word = error.right_word.lower()
    indexes = error.indexes
    description = error.description + " " + error2.description
    return Error(wrong_word, right_word, indexes, description, error.get_type())

def project_error(errors, error_to_project):
    project_type = error_to_project.get_type()
    if project_type not in error_types_to_concat:
        raise NotImplementedError("Trying to project an error of type {}, which is not allowed.".format(project_type))

    error_projectors = {
        "add_punc": add_punc,
        "del_punc": del_punc,
        "add_cap": add_cap,
        "del_cap": del_cap,
    }

    projected_errors = []

    for error in errors:
        projected_errors.append(error_projectors[project_type](error, error_to_project))
    
    return projected_errors

def check_if_list_of_errorList(lst):
    return isinstance(lst, list) and all(isinstance(item, ErrorList) for item in lst)

# Main function for error concatenation
def error_concatenator(errors, errors_to_project_onto_others, include_type=False):
    """
    Return sorted, listed and concatenated ErrorList
    """

    if not check_if_list_of_errorList(errors) and not check_if_list_of_errorList(errors_to_project_onto_others):
        raise NotImplementedError("Can only work with ErrorLists")

    errors_dict = errors_to_index_dict(errors)
    errors_to_project_dict = errors_to_index_dict(errors_to_project_onto_others)

    for key in errors_to_project_dict.keys():
        if key not in errors_dict.keys():
            errors_dict[key] = errors_to_project_dict[key]
        else:
            for error_to_project in errors_to_project_dict[key]:
                projected_errors = project_error(errors_dict[key], error_to_project)
                errors_dict[key] = projected_errors

    # In case of multiple errors_to_project on same indexes:
    final_errors = []
    for list_of_errors in errors_dict.values():
        first_error = list_of_errors[0]
        for additional_error in list_of_errors[1:]:
            first_error = project_error([first_error], additional_error)[0]
        final_errors.append(first_error)

    return ErrorList(final_errors).to_list(include_type=include_type, finalize=True)

class ErrorList():
    def __init__(self, lst = []) -> None:
        if isinstance(lst, ErrorList): lst = lst.errors; print("You passed a ErrorList instead of a list.")
        elif not isinstance(lst, list): raise ValueError("Parameter has to be a list.")
        self.errors = lst
        self.convert_lists_to_errors()
        self.is_healthy()

    def convert_lists_to_errors(self):
        self.errors = [error for error in self.errors if error is not None] 
        if len(self.errors) == 0: return None
        if isinstance(self.errors[0], Error): return None
        if len(self.errors[0]) != 5:
            raise ValueError(f"The errors list should have 5 columns, not {len(self.errors[0])}. Did you remember to: .to_list(include_type=True)?")
        self.errors = [Error(error[0], error[1], error[2], error[3], error[4]) for error in self.errors]

    def is_healthy(self):
        healthy_errors = [error.is_healthy() for error in self.errors]
        if len(healthy_errors) == 0: return True
        if not any([error.is_healthy() for error in self.errors]): raise ValueError(f"ErrorList is not healthy. Some errors have missing values.")
        return True

    def sort(self, errors): return sorted(errors, key=lambda x: x[2][1])
    def append(self, error): self.errors.append(error); self.is_healthy()

    def init_dict(self):
        def def_value(): return []
        return defaultdict(def_value)
    
    def concat_errors(self, errors):
        concated_errors = []
        dict = self.init_dict()
        for error in errors: dict[error[2]] += error
        for lst_of_errors in dict.values():
            if len(lst_of_errors) < 2: continue
            for error in lst_of_errors: concated_errors.append(error)

    def __add__(self, other):
        if not isinstance(other, ErrorList):
            return NotImplementedError("Can only add ErrorList + ErrorList")
        return ErrorList(self.errors + other.errors)
    
    def to_list(self, include_type=False, finalize=False):
        if finalize: errors_to_list = [error.to_finalized_list() for error in self.errors]
        else: errors_to_list = [error.to_list(include_type) for error in self.errors]
        true_errors = [error for error in errors_to_list if error is not None]
        return list(self.sort(true_errors))

class Error():
    def __init__(self, wrong_word: str = None, right_word: str = None, indexes: list = None, 
                       description: str = None, type: str = None) -> None:
        self.wrong_word = wrong_word
        self.right_word = right_word
        self.indexes = indexes
        self.description = description
        self.set_type(type)
    
    def from_list(self, lst): return Error(lst[0], lst[1], lst[2], lst[3], lst[4])
    def get_type(self): return self.__type

    def set_type(self, type):
        if type is None: pass
        elif type not in approved_types: raise ValueError(f"Type must be in {approved_types}")
        self.__type = type

    def get_description(self):
        """
        This function should be used on errors in concat_errors
        """
        if isinstance(self.wrong_word, list) or isinstance(self.right_word, list):
            return self.description
        if self.right_word[-1] in ",.!?":
            return self.description.replace("$wrong", self.wrong_word).replace("$right", self.right_word[:-1])
        return self.description.replace("$wrong", self.wrong_word).replace("$right", self.right_word)
    def is_healthy(self):
        if len([var_name for var_name, var_value in self.__dict__.items() if var_value is None]) == 0: return True
        return False

    def to_list(self, include_type=False):
        if self.is_healthy():
            if self.wrong_word == self.right_word: return None
            if include_type:
                return [self.wrong_word, self.right_word, self.indexes, self.description, self.get_type()]
            return [self.wrong_word, self.right_word, self.indexes, self.description]
        missing_instance_variables = [var_name for var_name, var_value in self.__dict__.items() if var_value is None]
        raise NotImplementedError(f"Error is not healthy. Please fill these variables: {[missing_instance_variables]}")

    def to_finalized_list(self): return [self.wrong_word, self.right_word, self.indexes, self.get_description()]
        
