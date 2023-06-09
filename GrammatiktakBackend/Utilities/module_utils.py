
class ModuleSequential():
    def __init__(self, modules, timeTracker):
        self.modules = modules
        self.timeTracker = timeTracker

    def correct_module(self, module, sentence, pos_tags, ner_tags, index_finder):
        errors = module.correct(sentence, pos_tags, ner_tags, index_finder)
        self.timeTracker.track(f"module {module.__class__.__name__}")
        return errors
    
    def correct(self, sentence, pos_tags, ner_tags, index_finder, ignore_indexes = False):
        index_finder.ignore_indexes = ignore_indexes
        return [self.correct_module(module, sentence, pos_tags, ner_tags, index_finder) for module in self.modules]
