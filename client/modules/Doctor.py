# vim: ai sw=4 expandtab:
import re
import time
from client import jasperpath
from client.utils.eliza import eliza

INSTANCE_WORDS = [ 
    'THE',
    'DOCTOR',
    'IS',
    'IN',
    'I',
    'FEEL',
    'HAPPY',
    'SAD',
    'WORRIED',
    'HURT',
    'WONDERFUL',
    'NERVOUS',
    'WORRIED',
    'PARANOID',
    'MYSELF',
    'MOTHER',
    'FATHER',
    'CAT',
    'DOG',
    'FISH',
    'LISTENING',
    'LISTEN',
    'YOU',
    'WHY',
    'WONT',
    'ARE',
]

WORDS = [ 'IS', 'THE', 'DOCTOR', 'IN' ]

PRIORITY = 50


def handle(text, mic, profile):
    """
    The doctor is in!
    """
    therapist = eliza()
     
    mic.say("What is on your mind today?")

    text = ''
    while not re.search(r'\bquit\b', text, re.IGNORECASE):
        text = mic.activeListen()
        if text != '':
            print text
            response = therapist.respond(text)
            print response
            mic.say(response)
        else:
            print "Got nothing"
    mic.say("I think we've made some real progress.  You'll get my bill in the mail.")

def isValid(text):
    """
    Responds to any phrase with the word "DOCTOR"
    """

    return bool(re.search(r'\bdoctor\b', text, re.IGNORECASE))
