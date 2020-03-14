# vim: ai sw=4 expandtab:
import logging
import re
from client.games import blackjack

WORDS = [ 'PLAY', 'BLACKJACK'  ]
NUMBERS = ['ZERO', 'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE', 'TEN', 'ELEVEN', 'TWELVE']
INSTANCE_WORDS = [ 'HIT', 'STAND', 'DOUBLE', 'SPLIT', 'YES', 'NO', 'QUIT' ] + NUMBERS


PRIORITY = 100

def handle(text, mic, profile):
    """
    Play Blackjack
    """

    logger = logging.getLogger(__name__)

    def in_func():
        retval = mic.activeListen().upper().split(' ')[0]
        if retval in NUMBERS:
            for i, numword in enumerate(NUMBERS):
                if retval == numword:
                    return str(i)
        else:
            return retval


    def out_func(string):
        print(string)
        mic.say(string)
     
    logger.info('Starting the Blackjack module')
    mic.say('Let\'s play Blackjack!')

    blackjack.play(input_func=in_func, output_func=out_func)

    mic.say('Thanks for playing Blackjack!')
    logger.info('Leaving Blackjack module')

def isValid(text):
    """
    "Play Blackjack"
    """

    return bool(re.search(r'\bblackjack\b', text, re.IGNORECASE))
