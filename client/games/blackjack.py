#!/usr/bin/env python
# vim: sw=4 ai expandtab

import logging
import random

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
        elif len(self) == 1:
            return str(self[0])
        else:
            return '{0} and {1}'.format(', '.join([str(card) for card in self[:-1]]), self[-1])

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

class Blackjack(object):
    def __init__(self):
        self.deck = Deck()
        self.deck.shuffle()
        self.hands = None

    def deal(self, num_players=1):
        self.num_players=num_players
        # hand #0 is the dealer
        num_hands = num_players + 1
        if (num_hands * 4) > self.deck.cardsLeft():
            print('Shuffling... because we only have {0} cards left'.format(self.deck.cardsLeft()))
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

if __name__ == '__main__':
    import sys
    game = Blackjack()

    def read_word():
        return sys.stdin.readline().strip().lower()

    def read_int(low_limit=None, high_limit=None):
        retval = None
        while retval is None:
            val = read_word()
            try:
                retval = int(val)
            except ValueError:
                print('{0} isn\'t a number.'.format(val))
            if low_limit is not None and retval < low_limit:
                print('Too low, try again')
                retval = None
            elif high_limit is not None and retval > high_limit:
                print('Too high, try again')
                retval = None
        return retval

    def read_answer(valid):
        retval = None
        while retval is None:
            retval = read_word()
            if retval not in valid:
                print('"{0}" isn\'t one of "{1}" or "{2}"'.format(retval, '", "'.join(valid[:-1]), valid[-1]))
                retval = None
        return retval

    keep_playing = 'yes'
    while keep_playing == 'yes':
        print('How many players?')
        n = read_int(low_limit=1, high_limit=10)
        game.deal(n)
        print('Dealer has a face down card and a {0}'.format(str(game.hand(0)[1])))
        done = set()
        while len(done) < n:
            for player in range(1,n+1):
                if player not in done:
                    print('Player {0} has {1} with a count of {2}'.format(
                        player,
                        str(game.hand(player)),
                        game.count(player)))
                    count = game.count(player)
                    if count < 21:
                        print('Hit or stand?')
                        ans = read_answer(['hit', 'stand'])
                        if ans == 'hit':
                            card, count = game.hit(player)
                            print('Player {0} got {1} for a count of {2}'.format(player, card, count))
                        else:
                            print('Player {0} standing at {1}'.format(player, count))
                            done.add(player)
                    if count == 21:
                        if len(game.hand(player)) == 2:
                            print('Blackjack!')
                        done.add(player)
                    if count > 21: 
                        print('Busted!')
                        done.add(player)

        dealer_count = game.count(0)
        print('Dealer reveals {0} which gives a count of {1}'.format(game.hand(0)[0], dealer_count))
        while dealer_count < 17:
            card, dealer_count = game.hit(0)
            print('Dealer is dealt {0} for a count of {1}'.format(card, dealer_count))
        if dealer_count > 21:
            print('Dealer busted!')
            winners = list(filter(lambda x: game.count(x) <= 21, range(1,n+1)))
            pushers = []
        else:
            print('Dealer standing at {0}'.format(dealer_count))
            winners = list(filter(lambda x: game.count(x) <= 21 and game.count(x) > dealer_count, range(1,n+1)))
            pushers = list(filter(lambda x: game.count(x) == dealer_count, range(1,n+1)))

        winners = [str(p) for p in winners]
        pushers = [str(p) for p in pushers]

        if not winners and not pushers:
            print('All players lost')
        else:
            if len(winners) == 1:
                print('Player {0} won!'.format(winners[0]))
            elif len(winners) > 1:
                print('Players {0} and {1} won!'.format(', '.join(winners[0:-1]), winners[-1]))
            if len(pushers) == 1:
                print('Player {0} pushed.'.format(pushers[0]))
            elif len(pushers) > 1:
                print('Players {0} and {1} pushed.'.format(', '.join(pushers[0:-1]), pushers[-1]))

        print("Play again?")
        keep_playing = read_answer(['yes', 'no', 'quit'])
