# vim: ai sw=4 expandtab:
import logging
import re
import time
from client import jasperpath
from client.zvm import ZorkMachine, ZorkPhone

logger = logging.getLogger(__name__)

WORDS = [
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
        "SECRET",
        "SELF",
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

WORDS += [ 'PLAY', 'MOONGLOW', 'MOON' ]

PRIORITY = 100

def handle(text, mic, profile):
    """
    Actually plays the game
    """

    mic.say('Lets play a game of moonglow')

    zvm = ZorkMachine('moonglow.z3')
    zorkphone = ZorkPhone(zvm, mic)
    zorkphone.talker.join()
    zorkphone.listener.join()

    mic.say('Thank you for making an old grue very happy.')

def isValid(text):
    """
    Responds to the phrase "PLAY MOONGLOW"
    """

    return bool(re.search(r'\bplay moon', text, re.IGNORECASE))
