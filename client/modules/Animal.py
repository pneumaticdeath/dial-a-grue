# vim: ai sw=4 expandtab:
import logging
import os
import re
from client import jasperpath
from client.games.animal import Animal

WORDS = [ 'PLAY', 'ANIMAL'  ]
INSTANCE_WORDS = [ 'YES', 'NO', 'REPEAT' ]
DIAL_NUMBER = '4'

PRIORITY = 100

def ask_yes_no(prompt, mic):
    valid_choices = ['YES', 'NO']
    print('Prompting with "{0}"'.format(prompt))
    answer = None
    while answer not in valid_choices:
        mic.say(prompt)
        answer = mic.activeListen().upper()
        answer = answer.split(' ')[0]
        dial_stack = mic.phone.dial_stack()
        if answer == 'REPEAT' or '7' in dial_stack:
            continue
        if '9' in dial_stack and '6' not in dial_stack:
            answer = "YES"
        elif '6' in dial_stack and '9' not in dial_stack:
            answer = "NO"
        elif answer not in valid_choices:
            print('Didn\'t like {0}, reprompting'.format(answer))
            mic.say('Sorry, I didn\'t catch that. Please answer yes, no, or ask to repeat the question.')
    return answer

def handle(text, mic, profile):
    """
    Play guess the animal
    """
     
    logging.info('Starting the Animal module')
    mic.say('Welcome to Guess The Animal.  Please think of an animal ' +
            'and I\'ll ask yes or no questions to try and guess it.')

    dbpath = os.path.join(jasperpath.APP_PATH, 'static', 'animals.db')

    game = Animal(dbfile=dbpath)
    
    keep_playing = ask_yes_no('Are you thinking of an animal?', mic);
    if keep_playing != 'YES':
        print('Not ready? later!')
        mic.say('Okay, come back when you\'ve thought of one!')
        return

    while keep_playing == 'YES':
        game.reset()
        questions_asked = 0
        while game.at_question():
            answer = ask_yes_no(game.current_node(), mic)
            questions_asked += 1
            if answer == 'NO':
                game.answer_no()
            elif answer == 'YES':
                game.answer_yes()
        answer = ask_yes_no('I think it\'s a {0}. Is that right?'.format(game.current_node()), mic)
        questions_asked += 1
        if answer == 'NO':
            print('Stumped me in {0} questions'.format(questions_asked))
            mic.say('Well, after {0} questions I guess you stumped me'.format(questions_asked))
        elif answer == 'YES':
            print('Guessed {0} correctly in {1} questions'.format(game.current_node(), questions_asked))
            mic.say('Cool, I figured out it was a {0} in {1} questions!'.format(game.current_node(), questions_asked))
        keep_playing = ask_yes_no('Play again?', mic)
    mic.say('Thanks for playing Guess the Animal with me!')
    logging.info('Leaving Animal module')

def isValid(text):
    """
    "Play Animal"
    """

    return bool(re.search(r'\banimal\b', text, re.IGNORECASE))
