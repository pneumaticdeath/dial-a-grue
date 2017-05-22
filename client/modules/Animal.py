# vim: ai sw=4 expandtab:
import logging
import re
from client import jasperpath
from client.animal import Animal

WORDS = [ 'YES', 'NO', 'PLAY', 'ANIMAL', 'QUIT' ]

PRIORITY = 50

def ask_yes_no(prompt, mic):
    valid_choices = ['YES', 'NO', 'QUIT']
    print('Prompting with "{0}"'.format(prompt))
    answer = None
    while answer not in valid_choices:
        mic.say(prompt)
        answer = mic.activeListen().upper()
        answer = answer.split(' ')[0]
        if answer not in valid_choices:
            print('Didn\'t like {0}, reprompting'.format(answer))
            mic.say('Sorry, I didn\'t catch that. Please answer yes or no.')
    return answer

def handle(text, mic, profile):
    """
    Repeats the user's input
    """
     
    logging.info('Starting the Animal module')
    mic.say('Welcome to Guess The Animal.  Please think of an animal' +
            'and I\'ll ask yes or no questions to guess it.')

    dbpath = os.path.join(jasperpath.APP_PATH, 'static', 'animals.db')

    game = Animal(dbfile=dbpath)
    
    keep_playing = 'YES'
    while keep_playing == 'YES':
        game.reset()
        while game.at_question():
            answer = ask_yes_no(game.current_node(), mic)
            if answer == 'NO':
                games.answer_no()
            elif answer == 'YES':
                games.answer_yes()
            elif answer == 'QUIT':
                keep_playing = 'NO'
                break;
        if keep_playing != 'YES':
            break
        answer = ask_yes_no('Is it a {0}?'.format(game.current_node()), mic)
        if answer == 'NO':
            print('Stumped me')
            mic.say('Well, I guess you stumped me')
        elif answer == 'YES':
            print('Guessed {0} correctly'.format(game.current_node()))
            mic.say('Cool, I figured out it was a {0}!'.format(game.current_node()))
        elif answer == 'QUIT':
            break
        keep_playing = ask_yes_no('Play again?', mic)
    mic.say('Thanks for playing Guess the Animal with me!')
    logging.info('Leaving Animal module')

def isValid(text):
    """
    Responds to the phrase "Play Animal"
    """

    return bool(re.search(r'\banimal\b', text, re.IGNORECASE))
