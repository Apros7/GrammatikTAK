
class ModuleSequential():
    def __init__(self, modules, timeTracker):
        self.modules = modules
        self.timeTracker = timeTracker

    def correct_module(self, module, sentence, pos_tags, ner_tags, index_finder):
        errors = module.correct(sentence, pos_tags, ner_tags, index_finder)
        self.timeTracker.track(f"module {module.__class__.__name__}")
        return errors
    
    def correct(self, sentence, pos_tags, ner_tags, index_finder, freeze_index_finder = False):
        index_finder.freeze() if freeze_index_finder else index_finder.unfreeze()
        return [self.correct_module(module, sentence, pos_tags, ner_tags, index_finder) for module in self.modules]

# Used if the module changes sentence, pos and ner
class ModuleSequentialWhenSentenceManipulation():
    def __init__(self, modules, timeTracker) -> None:
        self.modules = modules
        self.timeTracker = timeTracker

    def correct(self, sentence, pos_tags, ner_tags, index_finder):
        all_errors = [] # list of ErrorLists
        for module in self.modules:
            index_finder.freeze()
            module_errors, (sentence, pos_tags, ner_tags), index_finder = module.correct(sentence, pos_tags, ner_tags, index_finder)
            all_errors.append(module_errors)
            self.timeTracker.track(f"module {module.__class__.__name__}")
        return all_errors, (sentence, pos_tags, ner_tags), index_finder