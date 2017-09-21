# vim: ai sw=4 expandtab:
import logging
import pkgutil
import re
import time
from client import jasperpath

WORDS = [ 'REPEAT', 'AFTER', 'ME' ]
INSTANCE_WORDS = [
        'QUIT',
        'HELLO',
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
    Repeats the user's input
    """
     
    logging.info('Starting the Repeat module')
    mic.say("I'll repeat what you say until you say quit.")

    text = ''
    while not re.search(r'\bquit\b', text, re.IGNORECASE):
        text = mic.activeListen()
        if text:
            print text
            mic.say(text.lower())
        else:
            print "Got nothing"

    mic.say("Okay, goodbye!")
    logging.info('Leaving Repeat module')

def isValid(text):
    """
    Responds to the phrase "REPEAT AFTER ME"
    """

    return bool(re.search(r'\brepeat\b', text, re.IGNORECASE))
