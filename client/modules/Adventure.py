# vim: ai,sw=4,expandtab
import fcntl
import os
import pty
import re
import time
from client import jasperpath

ADV_WORDS = [
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
        'GRUE',
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
        'SUPERBRIEF',
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

WORDS = [ 'PLAY', 'ADVENTURE' ] + ADV_WORDS

PRIORITY = 100

class AdvMachine(object):
  
    def __init__(self):
        self._pid,self._fd = pty.fork()
        if self._pid == 0:
            # We need to exec adventure4, and it needs to run in its own dir
            os.chdir(os.path.join(jasperpath.APP_PATH, 'static', 'adventure4'))
            os.execv('./adventure4',['./adventure4',])
        else:
            flags = fcntl.fcntl(self._fd, fcntl.F_GETFL)
            fcntl.fcntl(self._fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
            print "Forked adventure4 in PID %d" % (self._pid,)


    def read(self):
        try:
            return os.read(self._fd, 30000)
        except OSError:
            return ''

    def write(self,str):
        return os.write(self._fd, str)
    
    def kill(self):
        os.kill(self._pid, 1)

    def is_running(self):
        try:
            os.kill(self._pid, 0)
        except OSError:
            return False
        return True

def handle(text, mic, profile):
    """
    Actually plays the game
    """

    mic.say('Lets play a game of adventure')

    adv = AdvMachine()
    time.sleep(1)

    while adv.is_running():
        adv_out = adv.read()
        print adv_out
        mic.say(adv_out)

        command = mic.activeListen()
        if command:
            command += '\n'
            # print command
            adv.write(command)
        else:
            print 'Didn\'t get anything'

def isValid(text):
    """
    Responds to the phrase "PLAY ADVENTURE"
    """

    return bool(re.search(r'\bplay adventure\b', text, re.IGNORECASE))
