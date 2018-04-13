# vim: ai sw=4 expandtab:
import logging
import os
import re
from client import jasperpath
from client.utils import text2int
from client.games.hammurabi import Hammurabi

def mk_upper(l):
    return [w.upper() for w in l]

WORDS = [ 'PLAY', 'HAMMURABI'  ]
INSTANCE_WORDS = [
    'YES',
    'NO',
    'QUIT',
    'NONE', 
] + mk_upper(text2int.units) + mk_upper(text2int.tens) + mk_upper(text2int.scales)

PRIORITY = 50

def get_number(prompt, mic):
    retval = None
    while retval is None:
        print(prompt)
        mic.say(prompt)
        heard = ''
        while not heard:
            heard = mic.activeListen()
        if heard == 'NONE':
            return 0
        try:
            retval = text2int.text2int(heard)
            if 'NO' == get_yes_no('I heard {0}, is that right?'.format(retval), mic):
                retval = None
        except ValueError as e:
            print(e)
            mic.say(str(e))
    return retval

def get_yes_no(prompt, mic):
    print(prompt)
    mic.say(prompt)
    answer = ''
    while answer not in ['YES', 'NO']:
        answer = mic.activeListen()
        if answer not in ['YES', 'NO']:
            print('Didn\'t like {0}'.format(answer))
            mic.say('That wasn\'t a yes or no.')
            mic.say(prompt)
    return answer

def handle(text, mic, profile):
    """
    Plays a game of Hammurabi
    """
     
    logging.info('Starting the Hammurabi module')
    mic.say('Welcome to Hammurabi\'s Babylon.  You will reign for {0} years.'.format(Hammurabi.reign))

    game = Hammurabi()
    
    last_year = 0
    while game.year <= game.reign and not game.overthrown:
        if last_year != game.year:
            print(game.status())
            mic.say(game.status())
            last_year = game.year
        else:
            print('Try again...')
            mic.say('Let\'s try that again!')
        print('Feed?')
        feed = get_number('How many bushels do you wish to feed to your people?', mic)
        print('Plant?')
        plant = get_number('How many acres would you like to plant?', mic)
        land = int((game.grain-feed-plant*game.seed_per_acre)/game.land_price)
        action = 'are able to buy' if land > 0 else 'will need to sell'
        mic.say('To do that you {0} {1} acres of land'.format(action, abs(land)))
        answer = get_yes_no('Is that what you\'d like to do?', mic)
        if answer == 'NO':
            print('Buy land?')
            land_bought = get_number('How many acres of land do you wish to buy?', mic)
            if land_bought == 0:
                print('Sell land?')
                land_sold = get_number('How many acres of land do you wish to sell?', mic)
                land = -land_sold
            else:
                land = land_bought
        print('land: {0}, feed: {1}, plant: {2}'.format(land, feed, plant))
        try:
            game.run(land, feed, plant)
        except ValueError as e:
            print(str(e))
            mic.say(str(e))
    mic.say(game.status())

    logging.info('Leaving Hammurabi module')

def isValid(text):
    """
    Responds to the phrase "Play Animal"
    """

    return bool(re.search(r'\bhammurabi\b', text, re.IGNORECASE))
