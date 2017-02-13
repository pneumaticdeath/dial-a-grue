# vim: ai sw=4 expandtab:
import fcntl
import os
import pty
import re
import time
from client import jasperpath

ZORK_WORDS = [
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
        'CANARY',
        'CASE',
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
        'FREEZE',
        'FROBIZZ',
        'FROBNOID',
        'FROBOZZLE',
        'FRY',
        'FUDGE',
        'FUMBLE',
        'GARLIC',
        'GET',
        'GO',
        'GOLD',
        'GRUE',
        'HELLO',
        'HI',
        'HOUSE',
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
        'KNIFE',
        'LADDER',
        'LAMP',
        'LARGE',
        'LEAFLET',
        'LEAVES',
        'LOOK',
        'MAIL',
        'MAILBOX',
        'MAP',
        'MOVE',
        'NEST',
        'NORTH',
        'NORTHEAST',
        'NORTHWEST',
        'OF',
        'OFF',
        'ON',
        'ONE',
        'OPEN',
        'PAINTING',
        'PICK',
        'PLATINUM',
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
        'SWITCH',
        'SWORD',
        'TABLE',
        'TAKE',
        'THE',
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
        'UP',
        'VERBOSE',
        'WATER',
        'WEST',
        'WINDOW',
        'WITH',
        'Y',
]

WORDS = [ 'PLAY', 'ZORK' ] + ZORK_WORDS

PRIORITY = 100

class ZorkMachine(object):
  
    def __init__(self):
        self._pid,self._fd = pty.fork()
        if self._pid == 0:
            # We need to exec the zvm, and it needs to run in its own dir
            os.chdir(os.path.join(jasperpath.APP_PATH, 'static', 'zvm'))
            os.execv('./zvm',['./zvm',])
        else:
            flags = fcntl.fcntl(self._fd, fcntl.F_GETFL)
            fcntl.fcntl(self._fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
            print "Forked zvm in PID %d" % (self._pid,)


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

def announce(text, mic):
    print text
    lines = text.split('\n')
    question_last = False
    for line in lines:
        line = line.strip()
        if line.endswith('?'):
            question_last = True
        elif line.endswith('.') or line.endswith('!'):
            question_last = False

        if line == '':
            time.sleep(0.25)
        elif line == '>':
            if not question_last:
                mic.say('What would you like to do?')
            return
        else:
            mic.say(line.lower())

def handle_quit(mic, zvm):
    """
    Handle when the user says QUIT
    """

    time.sleep(0.5)
    zvm_out = zvm.read()
    sub = 'Do you wish to leave the game? (Y is affirmative): >'
    repl = 'Do you wish to leave the game?'
    ind = zvm_out.find(sub)
    if ind >= 0:
        zvm_out = zvm_out[:ind] + repl + zvm_out[ind + len(sub):]
    announce(zvm_out, mic)

    if re.search(r'your score', zvm_out, re.IGNORECASE):
        resp = mic.activeListen()
        if 'YES' in resp.upper():
            return True
        else:
            zvm.write(resp)
            return False

def handle_save(mic, zvm):
    """
    Handle when the user says SAVE
    """
    pass # do nothing for now

def handle(text, mic, profile):
    """
    Actually plays the game
    """

    mic.say('Lets play a game of zork')

    zvm = ZorkMachine()
    time.sleep(1)

    zvm_out = zvm.read()
    print repr(zvm_out)
    zvm_out = '\r\n\r\n'.join(zvm_out.split('\r\n\r\n')[1:])
    announce(zvm_out, mic)

    while zvm.is_running():
        zvm_out = zvm.read()
        announce(zvm_out, mic)

        command = mic.activeListen()
        if command:
            zvm.write(command + '\n')
            if command.upper() == 'QUIT':
                if handle_quit(mic, zvm):
                    zvm.kill()
                    mic.say('That was a good game')
                    break
            elif command.upper() == 'SAVE':
                handle_save(mic, zvm)
        else:
            print 'Didn\'t get anything'

def isValid(text):
    """
    Responds to the phrase "PLAY ZORK"
    """

    return bool(re.search(r'\bplay zork\b', text, re.IGNORECASE))
