# vim: ai sw=4 expandtab:
import re
import logging


WORDS = [ 'HELLO' ]
DIAL_NUMBER = '44'

PRIORITY = 100

def handle(text, mic, profile):
    logging.info('Saying hello')
    mic.say('Hello there!')
    mic.say('Try dialing 1 or asking me what I can do.')

def isValid(text):
    return bool(re.search(r'\bhello\b', text, re.IGNORECASE))
