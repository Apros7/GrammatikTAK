import time

class ModuleTracker():
    """
    Used to track each module for:
    - time
    - corrections
    And upload to datastore for analyzing effectiveness of modules
    """

    def __init__(self): self.collection = {}
    def get(self): return self.collection
    def print(self): print(*list(self.get().items()), sep="\n"); print()
    def start_track(self): self.start_time = time.time()
    def init_new_sentence(self, original_sentence): self.reset(); self.sentence_length = len(original_sentence.split()) if len(original_sentence.split()) > 0 else 1
    def reset(self): self.collection = {}
        
    def end_track(self, module, errors): 
        key = module.__class__.__name__.split(".")[0].strip("'>")
        if key not in self.collection: self.collection[key] = {}
        self.collection[key]["time"] = (time.time() - self.start_time) / self.sentence_length
        self.collection[key]["corrections"] = len(errors) / self.sentence_length


class ModuleSequential():
    def __init__(self, modules, timeTracker, moduleTracker : ModuleTracker, use_models : bool ):
        self.modules = modules
        self.timeTracker = timeTracker
        self.moduleTracker = moduleTracker
        self.use_models = use_models

    def correct_module(self, module, sentence, pos_tags, ner_tags, index_finder):
        self.moduleTracker.start_track()
        errors = module.correct(sentence, pos_tags, ner_tags, index_finder)
        self.moduleTracker.end_track(module, errors)
        self.timeTracker.track(f"module {module.__class__.__name__}")
        return errors
    
    def correct(self, sentence, pos_tags, ner_tags, index_finder):
        index_finder.freeze()
        return [self.correct_module(module, sentence, pos_tags, ner_tags, index_finder) for module in self.modules]

# Used if the module changes sentence, pos and ner
class ModuleSequentialWhenSentenceManipulation():
    def __init__(self, modules, timeTracker, moduleTracker : ModuleTracker, use_models : bool) -> None:
        self.modules = modules
        self.timeTracker = timeTracker
        self.moduleTracker = moduleTracker
        self.use_models = use_models

    def correct(self, sentence, pos_tags, ner_tags, index_finder):
        all_errors = [] # list of ErrorLists
        for module in self.modules:
            index_finder.freeze()
            self.moduleTracker.start_track()
            module_errors, (sentence, pos_tags, ner_tags) = module.correct(sentence, pos_tags, ner_tags, index_finder)
            self.moduleTracker.end_track(module, module_errors)
            all_errors.append(module_errors)
            self.timeTracker.track(f"module {module.__class__.__name__}")
        return all_errors, (sentence, pos_tags, ner_tags)