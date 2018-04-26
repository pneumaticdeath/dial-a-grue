#!/usr/bin/env python
# vim: sw=4 ai expandtab
# Card library
# Copyright 2018, Mitch Patenaude

import logging
import random
import sys


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

