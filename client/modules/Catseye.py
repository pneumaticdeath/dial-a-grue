# vim: ai sw=4 expandtab:
import logging
import re
# import time
from client.games.zvm import ZorkMachine, ZorkPhone

logger = logging.getLogger(__name__)

INSTANCE_WORDS = [
        "ASH",
        "BASIN",
        "BENCH",
        "BLUE",
        "BOILER",
        "BOOK",
        "BOOKS",
        "CAT",
        "CATS",
        "CATSEYE",
        "CELLAR",
        "COUNTER",
        "DOOR",
        "DOWN",
        "DRINK",
        "DROP",
        "EAST",
        "ENTER",
        "EXAMINE",
        "EYE",
        "FILL",
        "FIREPLACE",
        "FROM",
        "GO",
        "HOLE",
        "IN",
        "INSERT",
        "INTO",
        "INVENT",
        "JAR",
        "LAB",
        "LIQUID",
        "LOOK",
        "LOOM",
        "ME",
        "MOVE",
        "NECKLACE",
        "NORTH",
        "OPEN",
        "PULL",
        "PUSH",
        "PUT",
        "QUIT",
        "REFRIGERATOR",
        "SELF",
        "SHELVES",
        "SOUTH",
        "SPOON",
        "TAKE",
        "TIE",
        "TO",
        "TOUCH",
        "TRAP",
        "UNLOCK",
        "UP",
        "VENT",
        "WEST",
        "WITH",
        "YARN",
]

WORDS = [ 'PLAY', 'CATSEYE' ]

PRIORITY = 100

def talker_quit(phone, zork_said):
    phone.announce('Okay, goodbye!')
    phone.running = False
    raise phone.StopGame()

def quit_handler(text, match, phone):
    logger.debug('Heard quit')
    phone.talker_handler = talker_quit
    phone.running = False

def save_handler(text, match, phone):
    logger.debug('Heard {0}'.format(text))
    phone.announce('This game doesn\'t support saving or restoring')

listen_handlers = [
    (re.compile(r'quit', re.IGNORECASE), quit_handler),
    (re.compile(r'save', re.IGNORECASE), save_handler),
    (re.compile(r'restore', re.IGNORECASE), save_handler),
]

def textmunge(text):
    replacements = [(r'Release \d+ \(\d+\) Inform v[\d.]+ microform v[\d.]+\r\n', '')]
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, re.MULTILINE)
    # text = '\n'.join([block.replace('\r\n',' ') for block in text.split('\r\n\r\n')])
    return text

def handle(text, mic, profile):
    """
    Play a game of cats eye
    """

    mic.say('Lets play a game of cats eye')

    zvm = ZorkMachine('catseye.z3')
    zorkphone = ZorkPhone(zvm, mic, 
                          munger=textmunge,
                          listen_handlers=listen_handlers)

    mic.say('Thank you for making an old grue very happy.')

def isValid(text):
    """
    "Play cats eye"
    """

    return bool(re.search(r'\bplay catseye', text, re.IGNORECASE))
