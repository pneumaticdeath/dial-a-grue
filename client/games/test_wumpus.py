#!/usr/bin/env python

import wumpus
import random

def test_map(mp, iterations=10000):
    endings = {}
    game = wumpus.Wumpus(mp)
    for _ in xrange(iterations):
        game.new_game()
        result = play_game(game)
        if result in endings:
            endings[result] += 1
        else:
            endings[result] = 1
    return endings

def play_game(game):
    while not game.game_over:
        dest = random.choice(game.map[game.player])
        look = game.look()
        if ' smell the wumpus' in look and random.randint(1,3) != 1:
            game.shoot([dest])
        else:
            game.move(dest)
    return game.game_over_msg

def print_result(name, result):
    print('    ----     {}     -----'.format(name))
    endings = result.keys()
    endings.sort(key=lambda a: result[a])
    for ending in endings:
        print('{}: {}'.format(ending, result[ending]))
    print('')

if __name__ == '__main__':
    map_results = {}
    for name, mp in wumpus.maps.items():
        map_results[name] = test_map(mp)

    names = map_results.keys()
    names.sort()
    for name in names:
        print_result(name, map_results[name])

