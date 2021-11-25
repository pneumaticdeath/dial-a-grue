# vim: ai sw=4 expandtab:
import logging
import random
import re
from client.games import wumpus

MAPS = [name.upper() for name in wumpus.maps.keys()]

WORDS = [ 'HUNT', 'THE', 'WUMPUS'  ] + MAPS

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
DIAL_NUMBER = '98'

PRIORITY = 100

instructions = [
    'Welcome to Hunt the Wumpus!',
    'In this game you are hunting the wiley (and smelly) wumpus.',
    'It is in one of the rooms in this cave system.',
    'In two rooms exist deep pits where you would fall to your death',
    'You can detect the presence of a pit by the breeze is causes in nearby rooms.',
    'In two other rooms reside bats, which if disturbed, will carry you off to another room.',
    'In order to kill the wumpus you must shoot it with one of your very crooked arrows.',
    'The arrows can be shot through up to 5 rooms, but that will wake the wumpus and it might move.',
    'There are many ways to die in the caves.  You can fall to your death, shoot yourself,',
    'run out of arrows, or be eaten by the wumpus.',
    'To move to a room, dial or say Move or Go followed by the room number.',
    'To shoot your arrows, dial or say Fire or Shoot followed by a list of room numbers.',
    'Now let\'s hunt the wumpus!',
]

DIAL_CHAR_MAP = {'1': re.compile(r'1'),         '2': re.compile(r'2|A|B|C'),   '3': re.compile(r'3|D|E|F'),
                 '4': re.compile(r'4|G|H|I'),   '5': re.compile(r'5|J|K|L'),   '6': re.compile(r'6|M|N|O'),
                 '7': re.compile(r'7|P|Q|R|S'), '8': re.compile(r'8|T|U|V'),   '9': re.compile(r'9|W|X|Y|Z'),
                 '*': re.compile(r'\*'),        '0': re.compile(r'0'),         '#': re.compile(r'#')}

    

def handle(text, mic, profile):
    """
    Hunt the smelly Wumpus
    """

    def output(string):
        print(string)
        mic.say(string)

    def input(expected=None):
        heard = None
        dial_stack = []
        r = None
        while not heard:
            heard = mic.activeListen().upper()
            dial_stack = mic.dial_stack()
            if expected and dial_stack:
                survivors = set(expected)
                for i, d in enumerate(dial_stack):
                    for s in expected:
                        if s in survivors and (i >= len(s) or not DIAL_CHAR_MAP[d].match(s[i].upper())):
                            survivors.remove(s)
                if len(survivors) == 1:
                    r = survivors.pop()
                    print("Dialed {}".format(r))
                    mic.say(r.lower())
                    if r.isdigit():
                        return [int(r)]
                    else:
                        return [r]
                elif survivors:
                    for x in survivors:
                        if len(x) == len(dial_stack):
                            logging.info('Assuming dial meant {}'.format(x))
                            mic.say(x.lower())
                            if x.isdigit():
                                return [int(x)]
                            else:
                                return [x]
                    output('Ambiguous! Dialed value could match {}'.format(' '.join(survivors)))
                else:
                    output('Dialed sequence didn\'t match anything I was expecting')
        parsed_words = []
        words = heard.split()
        for word in words:
            if word in NUMBERS:
                for i, numword in enumerate(NUMBERS):
                    if word == numword:
                        parsed_words.append(i)
                        break
            else:
                parsed_words.append(word)
        return parsed_words

    def ask_y_n(prompt):
        answer = None
        while answer is None:
            output(prompt)
            words = None
            while not words:
                words = input(['YES','NO'])
            answer = words[0]
            if answer not in ['YES', 'NO']:
                output('{0} wasn\'t a yes or no'.format(str(answer).lower()))
                answer = None
        return answer

    logging.info('Starting the Wumpus module')
    map_name = None
    for word in text.split():
        if word in MAPS:
            map_name = word.lower()
            break
    if map_name is None:
        map_name = random.choice(wumpus.maps.keys())
    wumpus_map = wumpus.maps[map_name]
    output('Let\'s Hunt the Wumpus on the {} map!'.format(map_name))

    game = wumpus.Wumpus(wumpus_map)

    answer = ask_y_n('Would you like instructions?')
    if answer == 'YES':
        for line in instructions:
            output(line)

    output(game.look())
    while not game.game_over:
        commands = input(['MOVE','GO','SHOOT','FIRE','LOOK'])
        if 'MOVE' in commands or 'GO' in commands:
            if type(commands[-1]) is int:
                output(game.move(commands[-1]))
                output(game.look())
            else:
                output('What is your destination?')
                output('Please say or dial a room number')
                adjacent = game.adjacent_rooms()
                rooms = input([str(i) for i in adjacent])
                if rooms and type(rooms[0]) is int:
                    output(game.move(rooms[0]))
                    output(game.look())
                else:
                    output('Didn\'t get a room number, please try again with a new command')
        elif 'SHOOT' in commands or 'FIRE' in commands:
            room_sequence = list(filter(lambda x: type(x) is int, commands))
            if room_sequence:
                output(game.shoot(room_sequence))
                output(game.look())
            else:
                output('Where do you want to shoot?')
                rooms = []
                output('Which room would you like to shoot into first? (dial or say it)')
                values = input(NUMBERS + [str(i) for i in range(1,21)])
                rooms.extend(filter(lambda x: type(x) is int, values))
                done = False
                while not done and len(rooms) < 5:
                    output('Which room should the arrow go to next? say or dial zero to end')
                    values = input(NUMBERS + [str(i) for i in range(21)])
                    if values and values[0] == 0:
                        done = True
                    else:
                        rooms.extend(filter(lambda x: type(x) is int, values))
                output(game.shoot(rooms))
                output(game.look())
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
    "Hunt the Wumpus"
    """

    return bool(re.search(r'\bwumpus\b', text, re.IGNORECASE))
