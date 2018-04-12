# vim: ai sw=4 expandtab:
import logging
import re
from client.games import blackjack

WORDS = [ 'PLAY', 'BLACKJACK'  ]
INSTANCE_WORDS = [ 'HIT', 'STAND', 'ONE', 'TWO', 'THREE', 'YES', 'NO', 'QUIT' ]

PRIORITY = 50

def handle(text, mic, profile):
    """
    plays Blackjack
    """

    def in_func():
        retval = mic.activeListen().lower().split(' ')[0]
        if retval == 'one':
            return '1'
        elif retval == 'two':
            return '2'
        elif retval == 'three':
            return '3'
        else:
            return retval


    def out_func(string):
        print(string)
        mic.say(string)
     
    logging.info('Starting the Blackjack module')
    mic.say('Let\'s play Blackjack!')

    blackjack.play(input_func=in_func, output_func=out_func)

    mic.say('Thanks for playing Blackjack!')
    logging.info('Leaving Blackjack module')

def isValid(text):
    """
    Responds to the phrase "Play Blackjack"
    """

    return bool(re.search(r'\bblackjack\b', text, re.IGNORECASE))
