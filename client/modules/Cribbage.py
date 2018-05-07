# vim: ai sw=4 expandtab:
import logging
import re
from client.games import cribbage
from client.games.utils import mk_print_list

WORDS = [ 'PLAY', 'CRIBBAGE'  ]
INSTANCE_WORDS = [ 'ACE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE', 'TEN', 'JACK', 'QUEEN', 'KING', 'OF', 'CLUBS', 'DIAMONDS', 'HEARTS', 'SPADES']


PRIORITY = 50

def handle(text, mic, profile):
    """
    Play Cribbage
    """

    def in_func():
        return mic.activeListen().lower().split()

    def out_func(string):
        print(string)
        mic.say(string)
     
    class PhonePlayer(cribbage.Player):

        def pickDiscards(self, my_crib):
            discards = cribbage.Hand()
            out_func('What would you like to discard first? {}'.format(mk_print_list(self.hand, conjunction='or')))
            discards.append(cribbage.input_card(self.hand, word_func=in_func, output=out_func))
            remaining = cribbage.Hand(self.hand)
            remaining.discard(discards[0])
            out_func('What next?')
            discards.append(cribbage.input_card(remaining, word_func=in_func, output=out_func))
            return discards

        def pickPeggingCard(self, choices, pegging_stack, pegging_count):
            if len(choices) == 1:
                out_func('Choosing {} for you, since it\'s the only card you can plan.'.foramt(choices[0]))
                return choices[0]
    
            out_func('What would you like to play for pegging? {}'.format(mk_print_list(choices, conjunction='or')))
            return cribbage.input_card(choices, word_func=in_func, output=out_func)


    logging.info('Starting the Cribbage module')
    mic.say('Let\'s play some Cribbage!')

    game = cribbage.Cribbage(playerclass=PhonePlayer)

    game.play(output=out_func)

    mic.say('Thanks for playing Cribbage!')
    logging.info('Leaving Cribbage module')

def isValid(text):
    """
    "Play Cribbage"
    """

    return bool(re.search(r'\bcribbage\b', text, re.IGNORECASE))
