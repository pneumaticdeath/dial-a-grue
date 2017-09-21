# vim: ai sw=4 expandtab:
import logging
import re
import time
from client import jasperpath
from client.zvm import ZorkMachine, ZorkPhone

logger = logging.getLogger(__name__)

INSTANCE_WORDS = [
        "ALIEN",
        "BARN",
        "COT",
        "DAMAGE",
        "DOOR",
        "DOWN",
        "DRAW",
        "DROP",
        "EAST",
        "ENTER",
        "EXAMINE",
        "EXIT",
        "FIELD",
        "FIX",
        "GET",
        "GIVE",
        "GLASS",
        "GLOVES",
        "GO",
        "HOUSE",
        "INVENTORY",
        "LAMP",
        "LAMPPOST",
        "LOOK",
        "MAKE",
        "MAP",
        "MAZE",
        "ME",
        "MOVE",
        "NORTH",
        "OF",
        "ORB",
        "PAPER",
        "PASSAGE",
        "PENCIL",
        "POST",
        "PUSH",
        "QUIT",
        "REPAIR",
        "RESTORE",
        "SAVE",
        "SECRET",
        # "SELF",
        "SHARD",
        "SHARPEN",
        "SOUTH",
        "STAIRS",
        "SUNGLASSES",
        "TAKE",
        "TEAR",
        "TO",
        "UP",
        "USING",
        "WAVE",
        "WEAR",
        "WEST",
        "WHEAT",
        "WINDOW",
        "WIRES",
        "WITH",
]

WORDS = [ 'PLAY', 'MOONGLOW', 'MOON' ]

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
    Actually plays the game
    """

    mic.say('Lets play a game of moon glow')

    zvm = ZorkMachine('moonglow.z3')
    zorkphone = ZorkPhone(zvm, mic, 
                          munger=textmunge,
                          listen_handlers=listen_handlers)
    zorkphone.talker.join()
    zorkphone.listener.join()

    mic.say('Thank you for making an old grue very happy.')

def isValid(text):
    """
    Responds to the phrase "PLAY MOONGLOW"
    """

    return bool(re.search(r'\bplay moon', text, re.IGNORECASE))
