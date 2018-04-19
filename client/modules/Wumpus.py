# vim: ai sw=4 expandtab:
import logging
import re
from client.games import wumpus

WORDS = [ 'HUNT', 'THE', 'WUMPUS'  ]
NUMBERS = [
  'ZERO',
  'ONE',
  'TWO',
  'THREE',
  'FOUR',
  'FIVE',
  'SIX',
  'SEVEN',
  'EIGHT',
  'NINE',
  'TEN',
  'ELEVEN',
  'TWELVE',
  'THIRTEEN',
  'FOURTEEN',
  'FIFTEEN',
  'SIXTEEN',
  'SEVENTEEN',
  'EIGHTEEN',
  'NINETEEN',
  'TWENTY',
]
INSTANCE_WORDS = [ 'LOOK', 'FIRE', 'SHOOT', 'MOVE', 'GO', 'YES', 'NO' ] + NUMBERS

PRIORITY = 50

def handle(text, mic, profile):
    """
    plays Hunt the Wumpus
    """

    def input():
        heard = mic.activeListen().upper()
        parsed_words = []
        for word in heard.split(' '):
            if word in NUMBERS:
                for i, numword in enumerate(NUMBERS):
                    if word == numword:
                        parsed_words.append(i)
                        break
                
            else:
                parsed_words.append(word)
        return parsed_words


    def output(string):
        print(string)
        mic.say(string)
     

    logging.info('Starting the Wumpus module')
    mic.say('Let\'s Hunt the Wumpus!')

    game = wumpus.Wumpus()

    output(game.look())
    while not game.game_over:
        commands = input()
        # if 'LOOK' in commands:
        #    output(game.look())
        if 'MOVE' in commands or 'GO' in commands:
            if type(commands[-1]) is int:
                output(game.move(commands[-1]))
                output(game.look())
            else:
                output('Couldn\'t make out a destination')
        elif 'SHOOT' in commands or 'FIRE' in commands:
            room_sequence = list(filter(lambda x: type(x) is int, commands))
            if room_sequence:
                output(game.shoot(room_sequence))
                output(game.look())
            else:
                output('Couldn\'t make out where to shoot')
        else:
            output('what?')

    mic.say('Thanks for Hunting the Wumpus!')
    logging.info('Leaving Wumpus module')

def isValid(text):
    """
    Responds to the phrase "Hunt the WUMPUS"
    """

    return bool(re.search(r'\bwumpus\b', text, re.IGNORECASE))
