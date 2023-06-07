
class ModuleSequential():
    def __init__(self, modules, timeTracker):
        self.modules = modules
        self.timeTracker = timeTracker

    def correct_module(self, module, sentence, pos_tags, ner_tags):
        errors = module.correct(sentence, pos_tags, ner_tags)
        self.timeTracker.track("module {}".format(module.__class__.__name__))
        return errors
    
    def correct(self, sentence, pos_tags, ner_tags):
        return [self.correct_module(module, sentence, pos_tags, ner_tags) for module in self.modules]
