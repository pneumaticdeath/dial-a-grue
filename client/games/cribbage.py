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

    def discard(self, card):
        for i, hand_card in enumerate(self):
            if hand_card == card:
                del self[i]
                return card
        return None

    def sortByRank(self):
        self.sort(key=lambda x: x._rank)

class GameOver(Exception):
    pass

class IllegalMove(Exception):
    pass

class Player(object):
    name = 'player'

    def __init__(self, winning_score=121):
        self.winning_score = winning_score
        self.reset()

    def reset(self):
        self.score = 0
        self.hand = Hand()
        self.pegging_hand = Hand()
        self.go = False

    def scores(self, amount):
        self.score += amount
        if self.score >= self.winning_score:
            raise GameOver()

    def startPegging(self):
        self.pegging_hand = Hand(self.hand)

class AIPlayer(Player):
    name = 'computer'

global __sublist_index_cache 
__sublist_index_cache = dict()

def sublists(input_list, size):
    key = (len(input_list), size)
    if key not in __sublist_index_cache:
        __sublist_index_cache[key] = expensive_sublists(range(len(input_list)), size)

    return [[input_list[ind] for ind in ind_subl]
            for ind_subl in __sublist_index_cache[key]]

def expensive_sublists(input_list, size):
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
    'ace': ('ace', 'aces'),
    '2': ('deuce', 'dueces'),
    '3': ('three', 'threes'),
    '4': ('four', 'fours'),
    '5': ('five', 'fives'),
    '6': ('six', 'sixes'),
    '7': ('seven', 'sevens'),
    '8': ('eight', 'eights'),
    '9': ('nine', 'nines'),
    '10': ('ten', 'tens'),
    'jack': ('jack', 'jacks'),
    'queen': ('queen', 'queens'),
    'king': ('king', 'kings'),
}

def is_run(cardlist):
    'Is the list a run'
    cardlist.sort(key=lambda x: x._rank)
    for idx in range(len(cardlist) - 1):
        if cardlist[idx]._rank + 1 != cardlist[idx+1]._rank:
            return False
    return True

def is_n_kind(cardlist):
    'Is this n of a kind'
    if len(cardlist) < 2:
        return False
    rankset = set()
    for card in cardlist:
        rankset.add(card.rank)
    return len(rankset) == 1

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

    # Check for 15s
    num_15s = 0
    for sublist_size in range(5, 1, -1):
        for sublist in sublists([crib_card] + hand, sublist_size):
            if sum_cards(sublist) == 15:
                num_15s += 1
    if num_15s > 0:
        count += 2*num_15s
        msgs.append(('{} fifteen{}'.format(num_15s, '' if num_15s == 1 else 's'), None, 2*num_15s))

    # Check for flush
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
            if is_n_kind(subset):
                score =  _n_kind_score[sublist_size]
                count += score
                if sublist_size == 2:
                    msgs.append(('pair', card_names[sublist[0].rank][1], 2))
                else:
                    msgs.append(('{} of a kind'.format(sublist_size), card_names[sublist[0].rank][1], score))
                    # Now prevent subsets 
                    for size_prime in range(sublist_size-1, 1, -1):
                        for sublist_prime in sublists(sublist, size_prime):
                            n_kind_exclusion.add(frozenset(sublist_prime))

    # Check for runs of <n>
    run_exclusions = set()
    for sublist_size in range(5, 2, -1):
        for sublist in sublists([crib_card] + hand, sublist_size):
            sublist.sort(key=lambda x: x._rank)
            if tuple(sublist) in run_exclusions:
                continue
            if is_run(sublist):
                count += sublist_size
                msgs.append(('run of {}'.format(sublist_size), '{} to {}'.format(card_names[sublist[0].rank][0],card_names[sublist[-1].rank][0]), sublist_size))
                if sublist_size > 3:
                    for x in range(3,sublist_size):
                        for y in range(sublist_size-x+1):
                            run_exclusions.add(tuple(sublist[y:y+x]))

    # Check for nobs
    if crib_card.rank != 'jack':
        for card in hand:
            if card.rank == 'jack' and card.suit == crib_card.suit:
                count += 1
                msgs.append(('nobs', None, 1))
                break

    return count, msgs

class Cribbage(object):
    def __init__(self):
        self.player = Player()
        self.ai = AIPlayer()
        self.crib_card = None
        self.crib = Hand()
        self.pegging_stack = []
        self.deck = cards.Deck()
        self.deck.shuffle()

    def chooseFirstCrib(self):
        player_card = None
        while player_card is None:
            player_card = self.deck.deal()
            ai_card = self.deck.deal()
            if player_card.rank == ai_card.rank:
                player_card = None
        self.players_crib = player_card._rank < ai_card._rank
        return player_card, ai_card

    def dealHands(self):
        self.player.hand = Hand()
        self.ai.hand = Hand()
        self.crib = Hand()
        self.crib_card = None
        self.deck.shuffle()
        for _ in xrange(6):
            self.noncrib_player.hand.append(self.deck.deal())
            self.crib_player.hand.append(self.deck.deal())

    def pickCribCard(self):
        self.crib_card = self.deck.deal()
        return self.crib_card

    def switchCrib(self):
        self.players_crib = not self.players_crib

    @property
    def crib_player(self):
        return self.player if self.players_crib else self.ai

    @property
    def noncrib_player(self):
        return self.ai if self.players_crib else self.player

    def startPegging(self):
        self.player.startPegging()
        self.ai.startPegging()
        self.pegging_turn, self.non_pegging_turn = (self.ai, self.player) if self.players_crib else (self.player, self.ai)
        self.resetPegging()

    def resetPegging(self):
        self.pegging_count = 0
        if self.player.pegging_hand:
            self.player.go = False
        if self.ai.pegging_hand:
            self.ai.go = False
        self.pegging_stack = Hand()

    def peg(self, card):
        if card_value(card) + self.pegging_count > 31:
            raise IllegalMove('pegging count would be greater than 31')
        self.pegging_stack.append(card)
        self.pegging_count += card_value(card)
        score, msgs = self.countPeggingStack()
        who = self.pegging_turn
        self.last_pegger = who
        if not self.non_pegging_turn.go and len(self.non_pegging_turn.pegging_hand) > 0:
            self.swapPeggers()
        return who, score, msgs # Calling routine is responible to taking the points

    def countPeggingStack(self):
        msgs = []
        score = 0
        if self.pegging_count == 15:
            score += 2 
            msgs.append(('fifteen', None, 2))

        for index in range(-len(self.pegging_stack), -1):
            substack = self.pegging_stack[index:]
            if len(substack) <= 4 and is_n_kind(substack):
                new_score = _n_kind_score[len(substack)]
                if len(substack) == 2:
                    msgs.append(('pair', card_names[substack[-1].rank][1], new_score))
                else:
                    msgs.append(('{} of a kind'.format(len(substack)), card_names[substack[-1].rank][1], new_score))
                score += new_score
                break # n_of_a_kind implies no runs
            if len(substack) >= 3 and is_run(substack):
                score += len(substack)
                msgs.append(('run of {}'.format(len(substack)), None, len(substack)))
                break
        return score, msgs

    def go(self):
        self.pegging_turn.go = True
        self.swapPeggers()

    def swapPeggers(self):
        self.non_pegging_turn, self.pegging_turn = self.pegging_turn, self.non_pegging_turn

def pick_best_discards(hand, my_crib, discards=None, best_score=-100, sample_size=10, full_deck=cards.Deck()):
    deck = filter(lambda x: x not in hand, full_deck.cards)
    sample_crib_cards = random.sample(deck, sample_size)
    for card1, card2 in sublists(hand, 2):
        new_score=0
        for tmp_crib in sample_crib_cards:
            tmp_hand = Hand(hand[:])
            tmp_hand.discard(card1)
            tmp_hand.discard(card2)
            score, msgs = count_hand(tmp_hand, tmp_crib, False)
            crib_score = discard_value([card1, card2])
            if my_crib:
                new_score += score + crib_score
            else:
                new_score += score - crib_score
        if new_score > best_score:
            discards = [card1, card2]
            best_score = new_score
    return discards
            
def discard_value(card_pair):
    value = 0
    if is_n_kind(card_pair):
        value += 2
    if card_value(card_pair[0]) + card_value(card_pair[1]) == 15:
        value += 2
    if abs(card_pair[0]._rank - card_pair[1]._rank) == 1:
        value += 1
    for card in card_pair:
        if card.rank == 'jack':
            value += 0.25
        elif card.rank == '5':
            value += 0.5
    return value

if __name__ == '__main__':

    def dump(hand, crib_card, is_crib=False):
        print(hand)
        s, m = count_hand(hand, crib_card, is_crib)
        print('Score: {}'.format(s))
        for x, y, z in m:
            if y is not None:
                print('{} of {} for {}'.format(x, y, z))
            else:
                print('{} for {}'.format(x, z))
        return s


    game = Cribbage()

    player_card, ai_card = game.chooseFirstCrib()
    print('Player cuts a {} and computer cuts a {}'.format(player_card, ai_card))

    try:
        hand_num = 0
        while game.player.score < 121 and game.ai.score < 121:
            hand_num += 1
            print('')
            print('Hand #{}'.format(hand_num))

            print('It\'s {}\'s crib.'.format(game.crib_player.name))

            game.dealHands()
            game.player.hand.sortByRank()
            print('You got {}'.format(game.player.hand))

            player_discards = pick_best_discards(game.player.hand, game.players_crib)

            print('You discarded {} and {}'.format(player_discards[0], player_discards[1]))
            for card in player_discards:
                game.crib.append(game.player.hand.discard(card))
            print('Leaving you with {}'.format(game.player.hand))

            ai_discards = pick_best_discards(game.ai.hand, not game.players_crib)

            for card in ai_discards:
                game.crib.append(game.ai.hand.discard(card))

            print('')
            game.pickCribCard()
            print('crib card: {:s}'.format(game.crib_card))
            if game.crib_card.rank == 'jack':
                game.crib_player.scores(2)
                print('{} scores 2 for his heels'.format(game.crib_player.name.capitalize()))

            # Pegging
            print('')
            print('Start of pegging')
            game.startPegging()
            game.player.pegging_hand.sortByRank()
            game.ai.pegging_hand.sortByRank()
            while game.player.pegging_hand or game.ai.pegging_hand:
                while game.pegging_count < 31 and (not game.player.go or not game.ai.go):
                    if game.pegging_turn.pegging_hand:
                        playable = Hand(filter(lambda x: card_value(x) + game.pegging_count <= 31, game.pegging_turn.pegging_hand))
                        if playable:
                            card = random.choice(playable)
                            who, score, msgs = game.peg(game.pegging_turn.pegging_hand.discard(card))
                            print('{} plays {} for a count of {}'.format(who.name.capitalize(), card, game.pegging_count))
                            for m in msgs:
                                if m[1] is not None:
                                    print('{} of {} for {}'.format(m[0], m[1], m[2]))
                                else:
                                    print('{} for {}'.format(m[0], m[2]))
                            if score:
                                who.scores(score)
                        else:
                            print('{} says "Go!"'.format(game.pegging_turn.name.capitalize()))
                            game.go()
                    else:
                        print('{} says "I\'m out"'.format(game.pegging_turn.name.capitalize()))
                        game.go()
                if game.pegging_count == 31:
                    print('{} gets 2'.format(game.last_pegger.name.capitalize()))
                    game.last_pegger.scores(2)
                else:
                    print('{} gets 1 for last card'.format(game.last_pegger.name.capitalize()))
                    game.last_pegger.scores(1)
                game.resetPegging()
                print('')

            # Count hands
            print('')
            print('{}\'s hand:'.format('Computer' if game.players_crib else 'Player'))
            score = dump(game.noncrib_player.hand, game.crib_card, False)
            game.noncrib_player.scores(score)
            print('')
            print('{}\'s hand:'.format('Computer' if not game.players_crib else 'Player'))
            score = dump(game.crib_player.hand, game.crib_card, False)
            game.crib_player.scores(score)
            print('')
            print('Crib:')
            score = dump(game.crib, game.crib_card, True)
            game.crib_player.scores(score)

            game.switchCrib()

            print('')
            print('Scores: player {} computer {}'.format(game.player.score, game.ai.score))

    except GameOver:
        pass

    print('Final scores: player {} computer {}'.format(game.player.score, game.ai.score))

    if game.player.score == game.ai.score:
        # impossible
        print('Tie')
    elif game.player.score > game.ai.score:
        print('Player wins')
        if game.ai.score < 61:
            print('Double Skunk!')
        elif game.ai.score < 91:
            print('Skunk!')
    else:
        print('Computer wins')
        if game.player.score < 61:
            print('Double Skunk!')
        elif game.player.score < 91:
            print('Skunk!')
    print('')
