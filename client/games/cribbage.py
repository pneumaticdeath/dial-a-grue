#!/usr/bin/env python
# vim: sw=4 ai expandtab
# Cribbage game
# Copyright 2018, Mitch Patenaude

import cards
import logging
import random
import sys
from utils import mk_print_list

class Hand(list):
    def __str__(self):
        if len(self) == 0:
            return 'an empty hand'
        else:
            return mk_print_list(self)

class Player(object):
    def __init__(self):
        self.hand = Hand()

class AIPlayer(Player):
    pass

def sublists(input_list, size):
    if not input_list or size <= 0:
        return [[],]
    if size >= len(input_list):
        return [input_list,]
    ret_list = []
    for index in xrange(len(input_list)-size+1):
        for sublist in sublists(input_list[index+1:], size-1):
            ret_list.append( input_list[index:index+1] + sublist )
    return ret_list

_n_kind_score = {2: 2, 3: 6, 4: 12}

card_names = {
    'ace': 'aces', 
    '2': 'deuces',
    '3': 'threes',
    '4': 'fours',
    '5': 'fives',
    '6': 'sixes',
    '7': 'sevens',
    '8': 'eights',
    '9': 'nines',
    '10': 'tens',
    'jack': 'jacks',
    'queen': 'queens',
    'king': 'kings',
}

def is_run(cardlist):
    'Is the list a run'
    cardlist.sort(key=lambda x: x._rank)
    for idx in range(len(cardlist) - 1):
        if cardlist[idx]._rank + 1 != cardlist[idx+1]._rank:
            return False
    return True

def card_value(card):
    if card._rank >= 10:
        return 10 
    else:
        return card._rank

def sum_cards(cardlist):
    card_sum = 0
    for card in cardlist:
        card_sum += card_value(card)
    return card_sum

def count_hand(hand, crib_card, is_crib=False):
    msgs = []
    count = 0
    suits = set()
    for card in hand:
        suits.add(card.suit)
    if len(suits) == 1:
        if crib_card.suit in suits:
            count += 5
            msgs.append(('flush royal', crib_card.suit, 5))
        elif not is_crib:
            count += 4
            msgs.append(('flush', suits.pop(), 4))

    # Check for <n> of a kind
    n_kind_exclusion = set()
    for sublist_size in range(4, 1, -1):
        for sublist in sublists([crib_card] + hand, sublist_size):
            subset = frozenset(sublist)
            if subset in n_kind_exclusion:
                continue
            rankset = set()
            for card in subset:
                rankset.add(card.rank)
            if len(rankset) == 1:
                score =  _n_kind_score[sublist_size]
                count += score
                if sublist_size == 2:
                    msgs.append(('pair', card_names[str(rankset.pop())], 2))
                else:
                    msgs.append(('{} of a kind'.format(sublist_size), card_names[str(rankset.pop())], score))
                    # Now prevent subsets 
                    for size_prime in range(sublist_size-1, 1, -1):
                        for sublist_prime in sublists(sublist, size_prime):
                            n_kind_exclusion.add(frozenset(sublist_prime))

    # Check for runs of <n>
    run_found = False
    run_exclusions = set()
    for sublist_size in range(5, 2, -1):
        for sublist in sublists([crib_card] + hand, sublist_size):
            sublist.sort(key=lambda x: x._rank)
            if tuple(sublist) in run_exclusions:
                continue
            if is_run(sublist):
                count += sublist_size
                msgs.append(('run of {}'.format(sublist_size), '{} to {}'.format(sublist[0].rank,sublist[-1].rank), sublist_size))
                if sublist_size > 3:
                    for x in range(3,sublist_size):
                        for y in range(sublist_size-x+1):
                            run_exclusions.add(tuple(sublist[y:y+x]))

    # Check for 15s
    num_15s = 0
    for sublist_size in range(5, 1, -1):
        for sublist in sublists([crib_card] + hand, sublist_size):
            if sum_cards(sublist) == 15:
                num_15s += 1
    if num_15s > 0:
        count += 2*num_15s
        msgs.append(('{} fifteens'.format(num_15s), None, 2*num_15s))

    # Check for nobs
    if crib_card.rank != 'jack':
        for card in hand:
            if card.rank == 'jack' and card.suit == crib_card.suit:
                count += 1
                msgs.append(('nobs', None, 1))
                break

    return count, msgs

if __name__ == '__main__':

    def dump(hand, crib_card, is_crib=False):
        print('hand {:s}'.format(hand))
        s, m = count_hand(hand, crib_card, is_crib)
        print('Score: {}'.format(s))
        for x, y, z in m:
            if y is not None:
                print('{} of {} for {}'.format(x, y, z))
            else:
                print('{} for {}'.format(x, z))

    deck = cards.Deck()
    deck.shuffle()

    crib_card = deck.deal()
    player_hand = Hand([deck.deal() for _ in range(4)])
    computer_hand = Hand([deck.deal() for _ in range(4)])
    crib = Hand([deck.deal() for _ in range(4)])

    print('crib card: {:s}'.format(crib_card))
    print('')
    print('Player hand:')
    dump(player_hand, crib_card, False)
    print('')
    print('Comptuer hand')
    dump(computer_hand, crib_card, False)
    print('')
    print('Crib')
    dump(crib, crib_card, True)

