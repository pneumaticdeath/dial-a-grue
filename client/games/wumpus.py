#!/usr/bin/env python
# vim: sw=4 ai expandtab
# Hunt the Wumpus, based on the basic game by Gregory Yob
# published by Creative Computing in 'More Basic Games' (1979)
# Copyright 2018, Mitch Patenaude

import random
import sys

map = {
    1: (2, 3, 11),
    2: (1, 5, 18),
    3: (1, 4, 6),
    4: (3, 5, 8),
    5: (2, 4, 10),
    6: (3, 7, 12),
    7: (6, 8, 14),
    8: (4, 7, 9),
    9: (8, 10, 15),
    10: (5, 9, 17),
    11: (1, 12, 20),
    12: (6, 11, 13),
    13: (12, 14, 19),
    14: (7, 13, 15),
    15: (9, 14, 16),
    16: (15, 17, 19),
    17: (10, 16, 18),
    18: (2, 17, 20),
    19: (13, 16, 20),
    20: (11, 18, 19),
}

def test_adjancency():
    'Make sure the graph is bidirectional'
    for room, neighbors in map.items():
        for adj_room in neighbors:
            assert room in map[adj_room], '{room} connects to {adj_room} but not vice versea'.format(room=room, adj_room=adj_room)

def mk_print_list(l, conjunction='and'):
    '''Makes a list of elements with of the form "a, b, c <conjucntion> d"'''

    if len(l) == 0:
        return ''
    if len(l) == 1:
        return str(l[0])
    else:
        return '{0} {1} {2}'.format(', '.join([str(w) for w in l[:-1]]), conjunction, l[-1])

class Wumpus(object):
    def __init__(self):
        self.new_game()

    def new_game(self):
        # initial rooms are (player, wumpus, 2 bats, 2 pits)
        self.init_rooms = random.sample(map.keys(), 6)
        self.restart()

    def restart(self):
        self.player = self.init_rooms[0]
        self.wumpus = self.init_rooms[1]
        self.bats = self.init_rooms[2:4]
        self.pits = self.init_rooms[4:6]
        self.arrows = 5
        self.wumpus_killed = False
        self.game_over = False
        self.game_over_msg = ''

    def look(self):
        if self.game_over:
            return 'Your game is over because {0}'.format(self.game_over_msg)

        msg = 'You are in room {0} in the cave.  There are passages to rooms {1}. '.format(self.player, mk_print_list(map[self.player]))

        wumpus_near = False
        pit_near = False
        bat_near = False
        for room in map[self.player]:
            if room == self.wumpus:
                wumpus_near = True
            if room in self.pits:
                pit_near = True
            if room in self.bats:
                bat_near = True
        warnings = []
        if bat_near:
            warnings.append('you hear bats nearby')
        if pit_near:
            warnings.append('you feel a breeze')
        if wumpus_near:
            warnings.append('you can smell the wumpus')
        msg += mk_print_list(warnings).capitalize()
        return msg

    def move(self, destination):
        if self.game_over:
            return 'Your game is over because {0}'.format(self.game_over_msg)

        if destination not in map[self.player]:
            return 'That room isn\'t connected to this one.'

        self.player = destination
        msgs = ['You move to room {0}'.format(destination)]

        while self.player in self.bats:
            # bat might carry you to the other bat
            self.player = random.choice(map.keys())
            msgs.append('a super bat carries you off to room {0}'.format(self.player))
            
        if self.player == self.wumpus:
            self._move_wumpus()
            if self.player == self.wumpus:
                msgs.append('you are devoured by the hungry wumpus')
                self.game_over = True
                self.game_over_msg = 'you have been eaten'
            else:
                msgs.append('you startle the wumpus who runs off')
        if self.player in self.pits:
            msgs.append('you fall to your death in a deep pit')
            self.game_over = True
            self.game_over_msg = 'you fell to your death'

        return mk_print_list(msgs)

    def shoot(self, path):
        if self.game_over:
            return 'Your game is over because {0}'.format(self.game_over_msg)

        if not path:
            return 'Well, that arrow went nowhere'
        elif len(path) > 5:
            return 'Can\'t shoot that far'

        self.arrows -= 1
        msgs = []
        current_room = self.player
        prior_room = None
        for room in path:
            if room == prior_room:
                msgs.append('It can\'t return to room {0} because your arrows aren\'t that crooked'.format(room))
                break
            if room not in map[current_room]:
                new_room = random.choice(map[current_room])
                msgs.append('There is no way for the arrow to get to room {0}, so it flies into {2} instead'.format(room, new_room))
                room = new_room
            else:
                msgs.append('The arrow flies to room {0}'.format(room))

            prior_room, current_room = current_room, room
            if current_room == self.wumpus:
                self.wumpus_killed = True
                self.game_over = True
                self.game_over_msg = 'you killed the Wumpus!'
                msgs.append('the arrow finds its mark and strikes the wumpus down!')
                return mk_print_list(msgs)
            elif current_room == self.player:
                self.game_over = True
                self.game_over_msg = 'you shot yourself'
                msgs.append('you shot yourself and lose')
                return mk_print_list(msgs)

        # shooting an arrow awakens the wumpus
        self._move_wumpus()
        if self.player == self.wumpus:
            self.game_over = True
            self.game_over_msg = 'you have been eaten'
            msgs.append('the wumpus stumbles into your room and devours you')
            return mk_print_list(msgs)
        else:
            msgs.append('you hear the wumpus move')

        left = 'a single arrow' if self.arrows == 1 else '{0} arrows'.format(self.arrows)
        msgs.append('you have {0} left'.format(left))

        if self.arrows < 1:
            self.game_over = True
            self.game_over_msg = 'you ran out of arrows'
            msgs.append('because you have no arrows left, you have lost')

        return mk_print_list(msgs)

    def _move_wumpus(self):
        wumpus_move_choices = list(map[self.wumpus])
        wumpus_move_choices.append(self.wumpus)
        self.wumpus = random.choice(wumpus_move_choices)

if __name__ == '__main__':
    test_adjancency()

    wumpus = Wumpus()
    while not wumpus.game_over:
        look = wumpus.look()
        print(look)
        dest = random.choice(map[wumpus.player])
        if ' smell the wumpus' in look and random.randint(1,3) != 1:
            print('shooting at {0}'.format(dest))
            print(wumpus.shoot([dest]))
        else:
            # print('moving to {0}'.format(dest))
            print(wumpus.move(dest))
    print(wumpus.look())