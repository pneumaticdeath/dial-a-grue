#!/usr/bin/env python
# vim: sw=4 ai expandtab
# Blackjack game
# Copyright 2018, Mitch Patenaude

import logging
import random
import sys

def mk_print_list(l, conjunction='and'):
    '''Makes a list of elements with of the form "a, b, c <conjucntion> d"'''

    if len(l) == 0:
        return ''
    if len(l) == 1:
        return str(l[0])
    else:
        return '{0} {1} {2}'.format(', '.join([str(w) for w in l[:-1]]), conjunction, l[-1])

class Card(object):
    suits = ['clubs', 'hearts', 'diamonds', 'spades']

    def __init__(self, rank, suit):
        if rank < 1 or rank > 13:
            raise ValueError('Bad rank {0}'.format(rank))
        self._rank = rank
        if suit not in self.suits:
            raise ValueError('Unknown suit {0}'.format(suit))
        self.suit = suit

    @property
    def rank(self):
        if self._rank == 1:
            return 'ace'
        elif self._rank == 11:
            return 'jack'
        elif self._rank == 12:
            return 'queen'
        elif self._rank == 13:
            return 'king'
        else:
            return str(self._rank)

    def __str__(self):
        return '{0} {1} of {2}'.format('an' if self._rank in [1, 8] else 'a', self.rank, self.suit)

    def __repr__(self):
        return '{0}({1}, {2})'.format(self.__class__.__name__, self._rank, repr(self.suit))

class Deck(object):
    def __init__(self):
        self.cards = []
        for suit in Card.suits:
            for rank in range(1,14):
                self.cards.append(Card(rank, suit))
        self.index = 0

    def shuffle(self):
        self.index = 0
        random.shuffle(self.cards)

    def deal(self):
        if self.index >= len(self.cards):
            raise StopIteration()
        card = self.cards[self.index]
        self.index += 1
        return card

    def cardsLeft(self):
        return len(self.cards) - self.index

    def __iter__(self):
        for card in self.cards:
            yield card

class Hand(list):
    def __str__(self):
        if len(self) == 0:
            return 'an empty hand'
        else:
            return mk_print_list(self)

def _count(hand):
    aces = 0
    count = 0
    for card in hand:
        if card._rank == 1:
            aces += 1
        elif card._rank >= 10:
            count += 10
        else:
            count += card._rank
    for x in range(aces):
        if count < 11:
            count += 11
        else:
            count += 1
    return count

class Dealer(object):
    def __init__(self):
        self.deck = Deck()
        self.deck.shuffle()
        self.hands = None

    def deal(self, num_players=1):
        self.num_players=num_players
        # hand #0 is the dealer
        num_hands = num_players + 1
        if (num_hands * 4) > self.deck.cardsLeft():
            self.deck.shuffle()
        self.hands = [Hand() for _ in range(num_hands)]
        for c in range(2):
            for h in range(num_hands):
                self.hands[h].append(self.deck.deal())

    def hand(self, player):
        return self.hands[player]

    def count(self, player):
        return _count(self.hand(player));

    def hit(self, player):
        new_card = self.deck.deal()
        self.hands[player].append(new_card)
        return new_card, self.count(player)

def read_line():
    return sys.stdin.readline()

def myprint(str):
    print(str)

def read_int(low_limit=None, high_limit=None, input_func=read_line, output_func=myprint):
    retval = None
    while retval is None:
        val = input_func().strip().lower()
        try:
            retval = int(val)
            if low_limit is not None and retval < low_limit:
                output_func('Too low, Please choose a number of {0} or greater'.format(low_limit))
                retval = None
            elif high_limit is not None and retval > high_limit:
                output_func('Too high, Please choose a number of {0} or less'.format(high_limit))
                retval = None
        except ValueError:
            output_func('{0} isn\'t a number.'.format(val))
    return retval

def read_answer(valid, input_func=read_line, output_func=myprint):
    retval = None
    while retval is None:
        retval = input_func().strip().lower()
        if retval in valid:
            return retval
        matches = list(filter(lambda x: x.startswith(retval), valid))
        if len(matches) > 1:
            output_func('{0} is ambiguous, could match {1}'.format(retval, mk_print_list(matches, 'or')))
            retval = None
        elif len(matches) == 0:
            output_func('{0} isn\'t one of {1}'.format(retval,mk_print_list(valid, 'or')))
            retval = None
    return matches[0]

def play(input_func=read_line, output_func=myprint):
    '''
plays a game of blackjack with up to 10 players.
Pass input_func and output_func with appropriate vectors for other implementations.
    '''

    dealer = Dealer()
    output_func('How many players?')
    n = read_int(low_limit=1, high_limit=10, input_func=input_func, output_func=output_func)
    keep_playing = 'yes'
    while keep_playing == 'yes':
        dealer.deal(n)
        output_func('Dealer has a face down card and {0}'.format(str(dealer.hand(0)[1])))
        for player in range(1,n+1):
            count = dealer.count(player)
            output_func('Player {0} has {1} with a count of {2}'.format(
                player,
                dealer.hand(player),
                count))
            done = False
            while not done:
                options = ['hit', 'stand']
                if len(dealer.hand(player)) == 2 and dealer.hand(player)[0].rank == dealer.hand(player)[1].rank:
                    options.append('double')
                if count < 21:
                    output_func('{0}?'.format(mk_print_list(options, 'or')))
                    ans = read_answer(options, input_func=input_func, output_func=output_func)
                    if ans == 'double':
                        output_func('don\'t know how yet')
                    elif ans == 'hit':
                        card, count = dealer.hit(player)
                        output_func('Player {0} got {1} for a count of {2}'.format(player, card, count))
                    else:
                        output_func('Player {0} standing at {1}'.format(player, count))
                        done = True
                if count == 21:
                    if len(dealer.hand(player)) == 2:
                        output_func('Blackjack!')
                    else:
                        output_func('Player {0} standing at 21'.format(player))
                    done = True
                if count > 21:
                    output_func('Busted!')
                    done = True
            output_func('')

        dealer_count = dealer.count(0)
        output_func('Dealer reveals {0} which gives a count of {1}'.format(dealer.hand(0)[0], dealer_count))
        while dealer_count < 17:
            card, dealer_count = dealer.hit(0)
            output_func('Dealer is dealt {0} for a count of {1}'.format(card, dealer_count))
        if dealer_count > 21:
            output_func('Dealer busted!')
            winners = list(filter(lambda x: dealer.count(x) <= 21, range(1,n+1)))
            pushers = []
        else:
            output_func('Dealer standing at {0}'.format(dealer_count))
            winners = list(filter(lambda x: dealer.count(x) <= 21 and dealer.count(x) > dealer_count, range(1,n+1)))
            pushers = list(filter(lambda x: dealer.count(x) == dealer_count, range(1,n+1)))

        # winners = [str(p) for p in winners]
        # pushers = [str(p) for p in pushers]

        if not winners and not pushers:
            output_func('All players lost')
        else:
            if len(winners) == 1:
                output_func('Player {0} won!'.format(winners[0]))
            elif len(winners) > 1:
                output_func('Players {0} won!'.format(mk_print_list(winners)))
            if len(pushers) == 1:
                output_func('Player {0} pushed.'.format(pushers[0]))
            elif len(pushers) > 1:
                output_func('Players {0} pushed.'.format(mk_print_list(winners)))

        output_func("Play again?")
        keep_playing = read_answer(['yes', 'no', 'quit'], input_func=input_func, output_func=output_func)

if __name__ == '__main__':
    play()
