# vim: ai sw=4 expandtab:
import fcntl
import os
import pty
import re
import time
from client import jasperpath

WORDS = [ 'REPEAT', 'AFTER', 'ME' ]

PRIORITY = 50

def handle(text, mic, profile):
    """
    Repeats the user's input
    """
     
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

def isValid(text):
    """
    Responds to the phrase "REPEAT AFTER ME"
    """

    return bool(re.search(r'\brepeat\b', text, re.IGNORECASE))
