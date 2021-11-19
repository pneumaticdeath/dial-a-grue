# vim: ai,sw=4,expandtab
import logging
import re
import time
from client.games.zvm import ZorkMachine, ZorkPhone, StopGame

logger = logging.getLogger(__name__)

INSTANCE_WORDS = [
        'ANCIENT',
        'AT',
        'ATTACK',
        'AXE',
        'BAG',
        'BAR',
        'BAUBLE',
        'BEAUTIFUL',
        'BIRD',
        'BLOODY',
        'BOTTLE',
        'BRACELET',
        'BRASS',
        'BREAK',
        'BRIDGE',
        'BRIEF',
        'BUILDING',
        'CANARY',
        'CHALICE',
        'CLIMB',
        'CLOSE',
        'COFFIN',
        'COINS',
        'CRYSTAL',
        'CUP',
        'DIAGNOSTIC',
        'DIAMOND',
        'DOOR',
        'DOWN',
        'DRINK',
        'DROP',
        'EAST',
        'EAT',
        'EGG',
        'EGYPTIAN',
        'EMERALD',
        'ENTER',
        'EXAMINE',
        'FALL',
        'FANTASIZE',
        'FEEBLE',
        'FENCE',
        'FERMENT',
        'FIERCE',
        'FIGURINE',
        'FIREPROOF',
        'FLOAT',
        'FLUORESCE',
        'FOLLOW',
        'FREEZE',
        'FROBIZZ',
        'FROBNOID',
        'FROBOZZLE',
        'FRY',
        'FUDGE',
        'FUMBLE',
        'GARLIC',
        'GATE',
        'GET',
        'GO',
        'GOLD',
        'GRATE',
        # 'GRUE',
        'HELLO',
        'HI',
        'HUGE',
        'IN',
        'INTO',
        'INVENTORY',
        'IVORY',
        'JADE',
        'JEWEL',
        'JEWELED',
        'JEWELS',
        'KEYS',
        'KILL',
        'LADDER',
        'LAMP',
        'LARGE',
        'LEAFLET',
        'LOOK',
        'MAILBOX',
        'MAP',
        'MOVE',
        'NEST',
        'NO',
        'NORTH',
        'NORTHEAST',
        'NORTHWEST',
        'OF',
        'OFF',
        'ON',
        'OPEN',
        'PAINTING',
        'PICK',
        'PLATINUM',
        'PLUGH',
        'POT',
        'PRAY',
        'PUT',
        'QUIT',
        'READ',
        'RESTART',
        'RESTORE',
        'ROPE',
        'RUG',
        'SACK',
        'SANDWICH',
        'SAPPHIRE',
        'SAVE',
        'SCARAB',
        'SCEPTRE',
        'SCORE',
        'SHOUT',
        'SILVER',
        'SKULL',
        'SMELL',
        'SOUTH',
        'SOUTHEAST',
        'SOUTHWEST',
        'STREAM',
        # 'SUPERBRIEF',
        'SWORD',
        'TABLE',
        'TAKE',
        'THROW',
        'TIE',
        'TO',
        'TORCH',
        'TRAP',
        'TREE',
        'TRIDENT',
        'TROLL',
        'TRUNK',
        'TURN',
        'UNLOCK',
        'UP',
        'VERBOSE',
        'WATER',
        'WEST',
        'WINDOW',
        'WITH',
        'XYZZY',
        'YES',
]

WORDS = [ 'PLAY', 'ADVENTURE' ]
DIAL_NUMBER = '23'

PRIORITY = 100

def quit_heard(phone, zork_said):
    logger.debug('quit_heard handler running')
    nuke_text = ' (Y is affirmative): >'
    ind = zork_said.find(nuke_text)
    if ind >= 0:
        zork_said = zork_said[:ind] + zork_said[ind + len(nuke_text):]
        phone.context['state'] = 'waiting_for_quit_confirmation'
    return zork_said
   
def quit_handler(text, match, phone):
    logger.debug('Heard quit')
    phone.talker_handler = quit_heard

def save_handler(text, match, phone):
    logger.debug('Heard save')
    phone.talker_handler = save_heard

def restore_handler(text, match, phone):
    logger.debug('Heard restore')
    phone.talker_handler = restore_heard

def save_heard(phone, zork_said):
    logger.debug('save_heard handler running')
    if 'Enter a file name' in zork_said:
        phone.announce('Saving')
        phone.zvm.write('\n')
        time.sleep(0.1)
        zork_said = phone.zvm.read()
        if 'Y/N' in zork_said:
            phone.zvm.write('y\n')
            zork_said = 'Overwrote old save'
    return zork_said

def restore_heard(phone, zork_said):
    logger.debug('restore_heard handler running')
    if 'Enter a file name' in zork_said:
        phone.announce('Loading')
        phone.zvm.write('\n')
        time.sleep(0.1)
        zork_said = phone.zvm.read()
    return zork_said

def default_listen_handler(text, match, phone):
    logger.debug('Default listen handler')
    if 'state' in phone.context and phone.context['state'] == 'waiting_for_quit_confirmation':
        return quit_confirm(text, match, phone)

def quit_confirm(text, match, phone):
    logger.debug('Waiting for quit confirmation')
    phone.context['state'] = None
    if text.upper() == 'YES':
        phone.running = False
        phone.zvm.write(text+'\n');
        phone.mic.say('That was a good game');
        raise StopGame()

listen_handlers = [
    (re.compile(r'quit', re.IGNORECASE), quit_handler),
    (re.compile(r'save', re.IGNORECASE), save_handler),
    (re.compile(r'restore', re.IGNORECASE), restore_handler),
    (re.compile(r'.'), default_listen_handler),  # The default handler NEEDS to be last.
]

def textmunge(text):
    replacements = [(r'Release 1 / Serial number 151001 / ZILF 0\.7 lib J3', ''),
                    (r'\(y/n\) >\r\n', 'Yes or no.\r\n')]
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, re.MULTILINE)
    #text = '\n'.join([block.replace('\r\n',' ') for block in text.split('\r\n\r\n')])
    return text

def handle(text, mic, profile):
    """
    Play Colossal Cave Adventure
    """

    mic.say('Lets play a game of adventure')

    zvm = ZorkMachine('advent.z3')
    zorkphone = ZorkPhone(zvm, mic, 
                          munger=textmunge,
                          listen_handlers=listen_handlers)

    mic.say('Thank you for making an old grue very happy.')

def isValid(text):
    """
    "Play adventure"
    """

    return bool(re.search(r'\bplay adventure\b', text, re.IGNORECASE))
