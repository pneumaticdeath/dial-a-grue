# vim: ai sw=4 expandtab:
import logging
import re
from client.games import blackjack

WORDS = [ 'PLAY', 'BLACKJACK'  ]
NUMBERS = ['ZERO', 'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE']
INSTANCE_WORDS = [ 'HIT', 'STAND', 'DOUBLE', 'SPLIT', 'YES', 'NO', 'QUIT' ] + NUMBERS
DIAL_NUMBER = '21'

DIAL_CHAR_MAP = {'1': re.compile(r'1'),         '2': re.compile(r'2|A|B|C'),   '3': re.compile(r'3|D|E|F'),
                 '4': re.compile(r'4|G|H|I'),   '5': re.compile(r'5|J|K|L'),   '6': re.compile(r'6|M|N|O'),
                 '7': re.compile(r'7|P|Q|R|S'), '8': re.compile(r'8|T|U|V'),   '9': re.compile(r'9|W|X|Y|Z'),
                 '*': re.compile(r'\*'),        '0': re.compile(r'0'),         '#': re.compile(r'#')}

PRIORITY = 100

def handle(text, mic, profile):
    """
    Play Blackjack
    """

    logger = logging.getLogger(__name__)

    def in_func(expected=None):
        retval = mic.activeListen().upper().split(' ')[0]
        dial_stack = mic.dial_stack()
        if expected is not None and dial_stack:
            survivors = set(expected)
            i = 0
            for i, d in enumerate(dial_stack):
                for s in expected:
                    if s in survivors and (i >= len(s) or not DIAL_CHAR_MAP[d].match(s[i].upper())):
                        survivors.remove(s)
            if len(survivors) == 1:
                r = survivors.pop()
                mic.say(r)
                logger.info('Dialed value matched {}'.format(r))
                return r
            elif survivors:
                mic.say('Ambiguous! Dialed value could match {}'.format(' '.join(survivors)))
                return ''
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
