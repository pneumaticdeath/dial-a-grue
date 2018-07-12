#!/usr/bin/env python
# vim: sw=4 ai expandtab
# Cribbage game
# Copyright 2018, Mitch Patenaude

from __future__ import print_function
import cards
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

    def __init__(self, game):
        self.game = game
        self.reset()

    def reset(self):
        self.score = 0
        self.hand = Hand()
        self.pegging_hand = Hand()
        self.go = False

    def scores(self, amount):
        self.score += amount
        if self.score >= self.game.winning_score:
            raise GameOver()

    def startPegging(self):
        self.pegging_hand = Hand(self.hand)

    def pickDiscards(self, my_crib):
        return pick_best_discards(self.hand, my_crib)

    def pickPeggingCard(self, choices, pegging_stack, pegging_count):
        return pick_best_pegging_card(choices, pegging_stack, pegging_count)

class AIPlayer(Player):
    name = 'computer'

class HumanPlayer(Player):
    name = 'human'

    def pickDiscards(self, my_crib):
        discards = Hand()
        print('What would you like to discard first? {}'.format(mk_print_list(self.hand, conjunction='or')))
        discards.append(input_card(self.hand))
        remaining_hand = Hand(self.hand)
        remaining_hand.discard(discards[0])
        print('What else would you like to discard? {}'.format(mk_print_list(remaining_hand, conjunction='or')))
        discards.append(input_card(remaining_hand))
        return discards

    def pickPeggingCard(self, choices, pegging_stack, pegging_count):
        if len(choices) == 1:
            print('Choosing {} for you, since it\'s the only card that you can play'.format(choices[0]))
            return choices[0]
        print('What do you want to play for pegging? {}'.format(mk_print_list(choices, conjunction='or')))
        return input_card(choices)

card_rank_mapping = {
    'ace':    1,
    'one':    1,
    '1':      1,
    'two':    2,
    'duece':  2,
    '2':      2,
    'three':  3,
    'trey':   3,
    '3':      3,
    'four':   4,
    '4':      4,
    'five':   5,
    '5':      5,
    'six':    6,
    '6':      6,
    'seven':  7,
    '7':      7,
    'eight':  8,
    '8':      8,
    'nine':   9,
    '9':      9,
    'ten':   10,
    '10':    10,
    'jack':  11,
    '11':    11,
    'queen': 12,
    '12':    12,
    'king':  13,
    '13':    13,
}

def card_suit_lookup(word):
    if word in cards.Card.suits:
        return word
    for suit in cards.Card.suits:
        if suit.startswith(word):
            return suit
    return None

def my_print(s):
    print(s)

def read_words():
    return sys.stdin.readline().strip().lower().split()

def input_card(possibilities, word_func=read_words, output=my_print):
    parsed_card = None
    while parsed_card is None:
        input_words = word_func()
        if not input_words:
            continue
        rank = input_words[1] if input_words[0] in ['a', 'an', 'the'] else input_words[0]
        suit = card_suit_lookup(input_words[-1])
        if rank in card_rank_mapping and suit is not None:
            try:
                parsed_card = cards.Card(card_rank_mapping[rank], suit)
            except Exception:
                output('Failed to parse {} of {}'.format(rank, suit))
        elif rank in card_rank_mapping:
            possible_rank = card_rank_mapping[rank]
            matches = list(filter(lambda x: x._rank == possible_rank, possibilities))
            if not matches:
                output('None of your choices match that')
                continue
            elif len(matches) == 1:
                parsed_card = matches[0]
            else:
                output('Which suit? {}?'.format(mk_print_list([c.suit for c in matches], conjunction='or')))
                input_words = word_func()
                if not input_words or input_words[0] == 'cancel':
                    continue
                elif card_suit_lookup(input_words[0]) in [c.suit for c in matches]:
                    parsed_card = cards.Card(possible_rank, card_suit_lookup(input_words[0]))
                else:
                    output('Didn\'t get that, let\'s start over')
        else:
            output('Did\'t understand "{}"'.format(' '.join(input_words)))
        if parsed_card is not None and parsed_card not in possibilities:
            output('"{}" isn\'t a legal play at this point.'.format(parsed_card))
            parsed_card = None
    return parsed_card

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
    def __init__(self, playerclass=Player, aiclass=AIPlayer, short_game=False):
        if short_game:
            self.winning_score = 61
            self.skunk_threshold = 31
            self.double_skunk_threshold = 1
        else:
            self.winning_score = 121
            self.skunk_threshold = 91
            self.double_skunk_threshold = 61
        self.player = playerclass(self)
        self.ai = aiclass(self)
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
        self.last_pegger = None
        self.pegging_turn, self.non_pegging_turn = (self.ai, self.player) if self.players_crib else (self.player, self.ai)
        self.resetPegging()

    def resetPegging(self):
        self.pegging_count = 0
        if self.player.pegging_hand:
            self.player.go = False
        if self.ai.pegging_hand:
            self.ai.go = False
        self.pegging_stack = Hand()
        if self.last_pegger == self.pegging_turn:
            self.swapPeggers()

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

    def printHand(self, hand, is_crib=False, output=my_print):
        output(hand)
        s, m = count_hand(hand, self.crib_card, is_crib)
        for x, y, z in m:
            if y is not None:
                output('{} of {} for {}'.format(x, y, z))
            else:
                output('{} for {}'.format(x, z))
        output('Score: {}'.format(s))
        return s

    def play(self, output=my_print):
        player_card, ai_card = self.chooseFirstCrib()
        output('{} cuts a {} and {} cuts a {}'.format(self.player.name.capitalize(), player_card, self.ai.name, ai_card))

        try:
            hand_num = 0
            while self.player.score < self.winning_score and self.ai.score < self.winning_score:
                hand_num += 1
                output('')
                output('Hand #{}'.format(hand_num))

                output('It\'s {}\'s crib.'.format(self.crib_player.name))

                self.dealHands()
                self.player.hand.sortByRank()
                # output('{} got {}'.format(self.player.name.capitalize(), self.player.hand))

                player_discards = self.player.pickDiscards(self.players_crib)

                output('{} discarded {} and {}'.format(self.player.name.capitalize(), player_discards[0], player_discards[1]))
                for card in player_discards:
                    self.crib.append(self.player.hand.discard(card))
                output('Leaving {} with {}'.format(self.player.name, self.player.hand))

                ai_discards = self.ai.pickDiscards(not self.players_crib)

                for card in ai_discards:
                    self.crib.append(self.ai.hand.discard(card))

                output('')
                self.pickCribCard()
                output('crib card: {:s}'.format(self.crib_card))
                if self.crib_card.rank == 'jack':
                    output('{} scores 2 for his heels'.format(self.crib_player.name.capitalize()))
                    self.crib_player.scores(2)

                # Pegging
                output('')
                output('Start of pegging')
                self.startPegging()
                self.player.pegging_hand.sortByRank()
                self.ai.pegging_hand.sortByRank()
                while self.player.pegging_hand or self.ai.pegging_hand:
                    while self.pegging_count < 31 and (not self.player.go or not self.ai.go):
                        if self.pegging_turn.pegging_hand:
                            playable = Hand(filter(lambda x: card_value(x) + self.pegging_count <= 31, self.pegging_turn.pegging_hand))
                            if playable:
                                # card = random.choice(playable)
                                card = self.pegging_turn.pickPeggingCard(playable, self.pegging_stack, self.pegging_count)
                                who, score, msgs = self.peg(self.pegging_turn.pegging_hand.discard(card))
                                output('{} plays {} for a count of {}'.format(who.name.capitalize(), card, self.pegging_count))
                                for m in msgs:
                                    if m[1] is not None:
                                        output('{} of {} for {}'.format(m[0], m[1], m[2]))
                                    else:
                                        output('{} for {}'.format(m[0], m[2]))
                                if score:
                                    who.scores(score)
                            else:
                                output('{} says "Go!"'.format(self.pegging_turn.name.capitalize()))
                                self.go()
                        else:
                            output('{} says "I\'m out"'.format(self.pegging_turn.name.capitalize()))
                            self.go()
                    if self.pegging_count == 31:
                        output('{} gets 2 for 31'.format(self.last_pegger.name.capitalize()))
                        self.last_pegger.scores(2)
                    else:
                        output('{} gets 1 for last card'.format(self.last_pegger.name.capitalize()))
                        self.last_pegger.scores(1)
                    self.resetPegging()
                    output('')

                # Count hands
                output('')
                output('Crib card again: {}'.format(self.crib_card))
                output('')
                output('{}\'s hand:'.format(self.noncrib_player.name.capitalize()))
                score = self.printHand(self.noncrib_player.hand, False, output=output)
                self.noncrib_player.scores(score)
                output('')
                output('{}\'s hand:'.format(self.crib_player.name.capitalize()))
                score = self.printHand(self.crib_player.hand, False, output=output)
                self.crib_player.scores(score)
                output('')
                output('Crib:')
                score = self.printHand(self.crib, True, output=output)
                self.crib_player.scores(score)

                self.switchCrib()

                output('')
                output('Scores: player {} computer {}'.format(self.player.score, self.ai.score))

        except GameOver:
            pass

        output('')
        output('Final scores: player {} computer {}'.format(self.player.score, self.ai.score))

        if self.player.score == self.ai.score:
            # impossible
            output('Somehow it\'s a tie!')
            self.loosing_score = None
        elif self.player.score > self.ai.score:
            output('Player wins')
            loosing_score = self.ai.score
        else:
            output('Computer wins')
            loosing_score = self.player.score
        if loosing_score < self.double_skunk_threshold:
            output('Double Skunk!')
        elif loosing_score < self.skunk_threshold:
            output('Skunk!')
        output('')

def pick_best_discards(hand, my_crib, discards=None, best_score=-100, sample_size=10, full_deck=cards.Deck()):
    deck = filter(lambda x: x not in hand, full_deck.cards)
    sample_crib_cards = random.sample(deck, sample_size)
    for card1, card2 in sublists(hand, 2):
        new_score=0
        crib_score = discard_value([card1, card2])
        for tmp_crib in sample_crib_cards:
            tmp_hand = Hand(hand[:])
            tmp_hand.discard(card1)
            tmp_hand.discard(card2)
            score, msgs = count_hand(tmp_hand, tmp_crib, False)
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
        if card.rank == 'jack':  # Heuristic for nobs
            value += 0.25
        elif card.rank == '5':  # Heuristic for 15
            value += 0.5
    return value

def pick_best_pegging_card(choices, pegging_stack, pegging_count):
    if len(choices) == 1:
        return choices[0]
    values = {}
    for choice in choices:
        value = 0
        new_count = card_value(choice) + pegging_count
        if new_count == 31:
            value += 2
        elif new_count == 15:
            value += 2
        elif new_count == 21:  # Heuristic to avoid 31
            value -= 0.5
        elif new_count == 10:  # Heuristic to avoid 15
            value -= 0.5
        elif new_count == 5:   # Heuristic to avoid 15
            value -= 0.5
        new_stack = pegging_stack + [choice]
        if len(new_stack) >= 3:
            for index in range(len(new_stack)-2):
                substack = new_stack[index:]
                if is_run(substack):
                    value += len(substack)
                    break
        if len(new_stack) >= 2:
            for index in range(len(new_stack)-1):
                substack = new_stack[index:]
                if is_n_kind(substack):
                    value += _n_kind_score[len(substack)]
                    break
        values[choice] = value
    best = sorted(values.values())[-1]
    best_choice = random.choice(filter(lambda x: values[x] == best, choices))
    return best_choice

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser('Cribbage')
    parser.add_argument('--interactive', action='store_true', default=False, help='Play an interactive game')
    parser.add_argument('--short-game', action='store_true', default=False, help='Play a short game (to 61)')
    args = parser.parse_args()

    if args.interactive:
        game = Cribbage(playerclass=HumanPlayer, short_game=args.short_game)
    else:
        game = Cribbage(short_game=args.short_game)

    game.play()

