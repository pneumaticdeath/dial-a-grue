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

instructions = [
    'Welcome to Hunt the Wumpus!',
    'In this game you are hunting the wiley (and smelly) wumpus.',
    'It is in one of the twenty rooms in this cave system.',
    'In two other rooms exist deep pits where you would fall to your death',
    'You can detect the presence of a cave by the breeze is causes in nearby rooms.',
    'In two other rooms reside bats, which if disturbed, will carry you off to another room.',
    'In order to kill the wumpus you must shoot it with one of your very crooked arrows.',
    'The arrows can be shot through up to 5 rooms, but that will wake the wumpus and it might move.',
    'There are many ways to die in the caves.  You can fall to your death, shoot yourself,',
    'run out of arrows, or be eaten by the wumpus.',
    'To move to a room say Move or Go followed by the room number.',
    'To shoot your arrows say Fire or Shoot followed by a list of room numbers.',
    'Now let\'s hunt the wumpus!',
]

    

def handle(text, mic, profile):
    """
    plays Hunt the Wumpus
    """

    def input():
        heard = None
        while not heard:
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
     
    def ask_y_n(prompt):
        answer = None
        while answer is None:
            output(prompt)
            words = None
            while not words:
                words = input()
            answer = words[0]
            if answer not in ['YES', 'NO']:
                output('{0} wasn\'t a yes or no'.format(answer))
                answer = None
        return answer

    logging.info('Starting the Wumpus module')
    mic.say('Let\'s Hunt the Wumpus!')

    game = wumpus.Wumpus()

    answer = ask_y_n('Would you like instructions?')
    if answer == 'YES':
        for line in instructions:
            output(line)

    output(game.look())
    while not game.game_over:
        commands = input()
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
        elif 'LOOK' in commands:
            output(game.look())
        else:
            output('what?')

        if game.game_over and not game.wumpus_killed:
            again = ask_y_n('Would you like to try again?')
            if again == 'YES':
                game.restart()
                output(game.look())


    mic.say('Thanks for Hunting the Wumpus!')
    logging.info('Leaving Wumpus module')

def isValid(text):
    """
    Responds to the phrase "Hunt the WUMPUS"
    """

    return bool(re.search(r'\bwumpus\b', text, re.IGNORECASE))
