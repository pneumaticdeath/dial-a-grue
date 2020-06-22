# vim: ai sw=4 expandtab:
import logging
import re
from client import tts

WORDS = [ 'CHANGE', 'VOICE'  ]
INSTANCE_WORDS = [ 'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE']

PRIORITY = 45

def handle(text, mic, profile):
    """
    Change the voice I use
    """
     
    logging.info('Changing voice')
    mic.say('Let\'s change my voice')
    
    mic.say('Which voice would you like? from one through nine')
    answer = mic.activeListen()
    while answer not in INSTANCE_WORDS:
        mic.say('I don\'t know voice {}'.format(answer))
        print('Don\'t know {}'.format(answer))
        mic.say('Which voice would you like?')
        answer = mic.activeListen()

    if answer == 'ONE':
        new_tts_engine = tts.get_engine_by_slug('espeak-tts')
    elif answer == 'TWO':
        new_tts_engine = tts.get_engine_by_slug('festival-tts')
    elif answer == 'THREE':
        new_tts_engine = tts.get_engine_by_slug('pico-tts')
    else:
        new_tts_engine = tts.get_engine_by_slug('flite-tts')

    new_tts = new_tts_engine.get_instance()

    if answer == 'FOUR':
        new_tts.voice = 'awb'
    elif answer == 'FIVE':
        new_tts.voice = 'rms'
    elif answer == 'SIX':
        new_tts.voice = 'slt'
    elif answer == 'SEVEN':
        new_tts.voice = 'kal'
    elif answer == 'EIGHT':
        new_tts.voice = 'kal16'

    mic.setSpeaker(new_tts)
    mic.say('Okay, now I talk like this')

def isValid(text):
    """
    "Change your voice"
    """

    return bool(re.search(r'\bvoice\b', text, re.IGNORECASE))
