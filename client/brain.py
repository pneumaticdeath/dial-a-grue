# -*- coding: utf-8-*-
import logging
import pkgutil
import jasperpath
import client.mic
import phone


class Brain(object):

    def __init__(self, mic, profile, active_stt_engine=None, echo=False):
        """
        Instantiates a new Brain object, which cross-references user
        input with a list of modules. Note that the order of brain.modules
        matters, as the Brain will cease execution on the first module
        that accepts a given input.

        Arguments:
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., phone
                   number)
        """

        self._logger = logging.getLogger(__name__)
        self.mic = mic
        self.profile = profile
        self.active_stt_engine = active_stt_engine
        self.modules = self.get_modules()
        self.dial_modules = self.get_dial_modules()
        self._logger.info("Found %s total modules and %s dialable modules",
                           len(self.modules), len(self.dial_modules))
        self.module_mics = dict()
        self._echo = echo

    @classmethod
    def get_modules(cls):
        """
        Dynamically loads all the modules in the modules folder and sorts
        them by the PRIORITY key. If no PRIORITY is defined for a given
        module, a priority of 0 is assumed.
        """

        logger = logging.getLogger(__name__)
        locations = [jasperpath.PLUGIN_PATH]
        logger.debug("Looking for modules in: %s",
                     ', '.join(["'%s'" % location for location in locations]))
        modules = []
        for finder, name, ispkg in pkgutil.walk_packages(locations):
            try:
                loader = finder.find_module(name)
                mod = loader.load_module(name)
            except:
                logger.warning("Skipped module '%s' due to an error.", name,
                               exc_info=True)
            else:
                if hasattr(mod, 'WORDS'):
                    logger.debug("Found module '%s' with words: %r", name,
                                 mod.WORDS)
                    modules.append(mod)
                else:
                    logger.warning("Skipped module '%s' because it misses " +
                                   "the WORDS constant.", name)
        modules.sort(key=lambda mod: mod.PRIORITY if hasattr(mod, 'PRIORITY')
                     else 0, reverse=True)
        return modules

    def query(self, texts):
        """
        Passes user input to the appropriate module, testing it against
        each candidate module's isValid function.

        Arguments:
        text -- user input, typically speech, to be parsed by a module
        """
        for module in self.modules:
            for text in texts:
                if module.isValid(text):
                    self._logger.debug("'%s' is a valid phrase for module " +
                                       "'%s'", text, module.__name__)
                    self.run_module(text, module)
                    return
        self._logger.debug("No module was able to handle any of these " +
                           "phrases: %r", texts)

    def run_module(self, text, module):
        try:
            if self.active_stt_engine is not None and hasattr(module, 'INSTANCE_WORDS'):
                self._logger.debug('Finding mic with instance words %s', ', '.join(module.INSTANCE_WORDS))
                if module.__name__ not in self.module_mics:
                    self._logger.debug('creating mic for module %s', module.__name__)
                    self.module_mics[module.__name__] = client.mic.Mic(
                        self.mic.speaker,
                        self.mic.passive_stt_engine,
                        self.active_stt_engine.get_module_instance(module),
                        echo=self._echo
                    )
                mic = self.module_mics[module.__name__]
            else:
                mic = self.mic
            module.handle(text, mic, self.profile)
        except phone.Hangup:
            self._logger.info('Module got hangup')
            print('Well fine! Just hang up on me')
        except Exception:
            self._logger.error('Failed to execute module',
                                exc_info=True)
            self.mic.say("I'm sorry. I had some trouble with " +
                            "that operation. Please try again later.")
        else:
            self._logger.debug("Handling of phrase '%s' by " +
                                "module '%s' completed", text,
                                module.__name__)

    def get_dial_modules(self):
        dial_modules = {}
        for mod in self.modules:
            if hasattr(mod, 'DIAL_NUMBER'):
                dial_number = mod.DIAL_NUMBER
                self._logger.debug("module %s has dial number '%s'",mod.__name__, dial_number)
                dial_modules[dial_number] = mod
        return dial_modules

    def dial(self, number, texts):
        try:
            if number in self.dial_modules:
                self.run_module(texts[0], self.dial_modules[number])
            else:
                self._logger.debug("Unable to dial number '%s'", number)
                self.mic.say("The extension {} is unknown, please dial 1 for help"
                             .format(number))
        except phone.Hangup:
            self._logger.info("Module got hangup")
            print("Well, that was rude");
        except Exception:
            self._logger.error("Failed to load module", exc_info=True)
            self.mic.say("I'm sorry, that extension is not available right now")
