# vim: ai sw=4 expandtab:
import re
import logging
import pkgutil
from client import jasperpath, phone


WORDS = [ 'WHAT', 'CAN', 'YOU', 'DO' ]
INSTANCE_WORDS = WORDS
DIAL_NUMBER = '1'

PRIORITY = 100

def handle(text, mic, profile):
    mic.say('What can I do?!?')
    actions = {}
    locations = [jasperpath.PLUGIN_PATH]
    for finder, name, ispkg in pkgutil.walk_packages(locations):
        if name == __name__:
            continue

        try:
            loader = finder.find_module(name)
            mod = loader.load_module(name)
            if hasattr(mod.handle, '__doc__') and hasattr(mod.isValid, '__doc__'):
                dial_number = mod.DIAL_NUMBER if hasattr(mod, 'DIAL_NUMBER') else None
                actions[(dial_number, mod.isValid.__doc__)] = mod.handle.__doc__
        except:
            logging.warning('Skipped loading module {0}'.format(name), exc_info=True)

    if not actions:
        print('Didn\'t get anything')
        mic.say('Not much apparently...')
    else:
        for pair, result in actions.items():
            number, phrase = pair
            if phrase and result:
                if number is not None:
                    print('({0}) {1} -> {2}'.format(number, phrase.strip(), result.strip()))
                    mic.say('If you dial {0}, or say {1}, then you can {2}'
                            .format(number, phrase, result))
                else:
                    print('{0} -> {1}'.format(phrase.strip(), result.strip()))
                    mic.say('If you say {0}, then you can {1}.'.format(phrase, result))
                if mic.phone.on_hook():
                    raise phone.Hangup()
        print('That\'s all folks!')
        mic.say('And that\'s it... have fun!')

def isValid(text):
    return bool(re.search(r'\bwhat\b', text, re.IGNORECASE))
