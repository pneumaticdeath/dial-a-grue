# vim: ai sw=4 expandtab:
import logging
import os
import pkgutil
import random
import re
import tempfile
from client import jasperpath

WORDS = [ 'REPEAT', 'AFTER', 'ME' ]

INSTANCE_WORDS = [
        'QUIT',
        'HELLO',
        'TRAIN',
    ]

INSTANCE_WORDS.extend(WORDS)
locations = [jasperpath.PLUGIN_PATH]
for finder, name, ispkg in pkgutil.walk_packages(locations):
    if name == __name__:
        continue

    try:
        loader = finder.find_module(name)
        mod = loader.load_module(name)
    except:
        logging.warning('Skipped repeat of module %s\'s words', name, exc_info=True)
    else:
        if hasattr(mod, 'WORDS'):
            INSTANCE_WORDS.extend(mod.WORDS)
        if hasattr(mod, 'INSTANCE_WORDS'):
            INSTANCE_WORDS.extend(mod.INSTANCE_WORDS)

PRIORITY = 50

def handle(text, mic, profile):
    """
    have what you say repeated
    """
     
    logging.info('Starting the Repeat module')
    mic.say("I'll repeat what you say until you say quit.")

    text = ''
    while not re.search(r'\bquit\b', text, re.IGNORECASE):
        text = mic.activeListen()
        if text:
            print text
            mic.say(text.lower())
            if re.search(r'\btrain\b', text, re.IGNORECASE):
                mic.keep_files = True
                done = False
                test_data = tempfile.NamedTemporaryFile(prefix='test_', suffix='.txt', delete=False)
                print('Training mode!')
                mic.say('Entering training mode')
                print('Trainning data in {0}'.format(test_data.name))
                while not done:
                    target_word = random.choice(INSTANCE_WORDS)
                    print('Target word: {0}'.format(target_word))
                    mic.say('Please say {0}'.format(target_word.lower()))
                    text = mic.activeListen()
                    if re.search(r'\bquit\b', text, re.IGNORECASE) and target_word != 'QUIT':
                        done = True
                    else:
                        test_data.write('{0},{1},{2}\n'.format(target_word, text, mic.last_file_recorded))
                        if text.lower() == target_word.lower():
                            print('Matched')
                            mic.say('Understood')
                        else:
                            print('Got {0} instead'.format(text))
                            mic.say('I heard you say {0}'.format(text.lower()))
                mic.keep_files = False
                os.remove(mic.last_file_recorded)
        else:
            print "Got nothing"

    mic.say("Okay, goodbye!")
    logging.info('Leaving Repeat module')

def isValid(text):
    """
    "Repeat after me"
    """

    return bool(re.search(r'\brepeat\b', text, re.IGNORECASE))
