#!/usr/bin/env python
# vim: sw=4 ai expandtab

import logging
import sqlite3
import sys

class Node(object):
    @classmethod
    def find(cls, node_id, connection):
        results = connection.execute('SELECT ROWID, node_text, yes_node, no_node '
                                     'FROM animals where ROWID = ?', (node_id,))
        first = True
        new_node_id = None
        for result in results:
            if first:
                new_node_id, node_text, yes_node, no_node = result
                first = False
            else:
                # This shouldn't be possible
                logging.warning("Got more than 1 row with ROWID %d" % (node_id))
                break
        if new_node_id != node_id :
            raise RuntimeError('Got new_node_id %s instead of %s' % (new_node_id, node_id))
        return cls(connection, new_node_id, node_text, yes_node, no_node)

    @classmethod
    def create(cls, node_text, connection, node_id = None):
        if node_id is None:
            cursor = connection.cursor()
            result = cursor.execute('INSERT INTO animals (node_text) values (?);', (node_text,))
            node_id = cursor.lastrowid
        else:
            result = connection.execute('INSERT INTO animals (rowid, node_text) values (?,?);',
                                        (node_id, node_text))
        connection.commit()        
        return cls.find(node_id, connection)

    @classmethod
    def _create_db(cls, conn):
        res = conn.execute('CREATE TABLE animals (node_text TEXT NOT NULL, yes_node INT, no_node INT);')
	conn.commit()
        return cls.create('Horse', conn, 1)

    def __init__(self, connection, node_id, node_text, yes_node, no_node):
        self._conn = connection
        self.node_id = node_id
        self.node_text = node_text
        self.yes_node = yes_node
        self.no_node = no_node

    def update(self, node_text, yes_node, no_node):
        cursor = self._conn.cursor()
        cursor.execute('UPDATE animals SET node_text = ?, yes_node = ?, no_node = ? WHERE rowid = ?;', (node_text, yes_node, no_node, self.node_id))
        self._conn.commit()
        self.node_text = node_text
        self.yes_node = yes_node
        self.no_node = no_node

class Animal(object):
    def __init__(self, allow_updates=True, dbfile=None):
        self._updates = allow_updates
        if dbfile is None:
            logging.debug('Creating in-memory database')
            self._conn = sqlite3.connect(':memory:')
        else:
            self._conn = sqlite3.connect(dbfile)
        self._tree = Tree(self._conn)
        self.reset()

    def reset(self):
        try:
            self._current_node = Node.find(1, self._conn)
        except sqlite3.OperationalError as e:
            self._current_node = Node._create_db(self._conn)

    def current_node(self):
        return self._current_node.node_text

    def at_question(self):
        return self._current_node.yes_node is not None and self._current_node.no_node is not None

    def answer_yes(self):
        if self._current_node.yes_node is not None:
            self._current_node = Node.find(self._current_node.yes_node, self._conn)
        else:
            raise RuntimeError('node {0} ("{1}") is a leaf node'.format(self._current_node.node_id, self._current_node.node_text))

    def answer_no(self):
        if self._current_node.no_node is not None:
            self._current_node = Node.find(self._current_node.no_node, self._conn)
        else:
            raise RuntimeError('node {0} ("{1}") is a leaf node'.format(self._current_node.node_id, self._current_node.node_text))

    def update(self, new_animal, new_question, is_yes):
        if is_yes:
            yes_node = Node.create(new_animal, self._conn)
            no_node = Node.create(self._current_node.node_text, self._conn)
        else:
            yes_node = Node.create(self._current_node.node_text, self._conn)
            no_node = Node.create(new_animal, self._conn)
        self._current_node.update(new_question, yes_node.node_id, no_node.node_id)

    def search(self, name):
        return self._tree.search(name)

class Tree(object):
    def __init__(self, db):
        if type(db) is str:
            self._conn = sqlite3.connect(db)
        else:
            self._conn = db

    def walk(self, depth_first=False):
        nodes = []
        nodes.append((1, [], Node.find(1, self._conn)))
        while len(nodes) > 0:
            depth, seq, node = nodes[0]
            nodes = nodes[1:]
            if node.yes_node:
                new_nodes = [(depth+1, seq + [('yes', node.node_text)], Node.find(node.yes_node, self._conn)),
                             (depth+1, seq + [('no', node.node_text)], Node.find(node.no_node, self._conn))]
                if depth_first:
                    nodes = new_nodes + nodes
                else:
                    nodes.extend(new_nodes)
            yield depth, seq, node

    def search(self, name):
        for depth, seq, node in self.walk():
            if not node.yes_node and node.node_text.lower().strip() == name.lower().strip():
                return seq
        return []


if __name__ == '__main__':
    import argparse
    import os

    def read_y_n(prompt=''):
        if prompt:
            print(prompt)
        answer = sys.stdin.readline().lower().strip()
        while answer not in ['yes', 'y', 'no', 'n']:
            print('Please answer "Yes" or "No". {0} '.format(prompt))
            answer = sys.stdin.readline().lower().strip()
        return answer

    dbfile_default = os.path.join(os.path.dirname(__file__), '..', 'static', 'animals.db')
    parser = argparse.ArgumentParser('Play a game of Animal')
    parser.add_argument('--database', default=dbfile_default, help='Database file')
    args = parser.parse_args()

    game = Animal(allow_updates=True, dbfile=args.database)
    keep_playing = 'yes'
    while keep_playing.startswith('y'):
        question_count=0
        sequence = []
        print('Think of an animal!')
        while game.at_question():
            question_count += 1
            answer = read_y_n(game.current_node())
            if answer.startswith('y'):
                sequence.append('yes')
                game.answer_yes()
            elif answer.startswith('n'):
                sequence.append('no')
                game.answer_no()
            else:
                raise RuntimeError("Got unexpected answer '{0}'".format(answer))
        question_count += 1
        answer = read_y_n('I think it\'s a {0}. Is that right?'.format(game.current_node()))
        if answer.startswith('n'):
            print('Well.. I asked you {0} questions and you stumped me.  What was it? '
                  .format(question_count))
            new_animal = sys.stdin.readline().strip()
            while new_animal.endswith('?') or not new_animal:
                print('Sorry, I didn\'t get that.  What kind of animal was it again? ')
                new_animal = sys.stdin.readline().strip()
            if new_animal.lower().startswith('a '):
                new_animal = new_animal[2:]
            elif new_animal.lower().startswith('an '):
                new_animal = new_animal[3:]
            existing = game.search(new_animal)
            if existing:
                if new_animal.strip().lower() == game.current_node().lower():
                    print("That's what I said!")
                else:
                    for x in range(min(len(existing),len(sequence))):
                        searched_answer, searched_node = existing[x]
                        given_answer = sequence[x]
                        if searched_answer != given_answer:
                            print('I thought the answer to "{0}" for a {1} is {2}!'.format(searched_node, new_animal, searched_answer))
                            break
            else:
                print('What is a yes/no question that would distinguish a {0} from a {1}?\n'
                      .format(game.current_node(), new_animal))
                new_question = sys.stdin.readline().strip()
                if not new_question.endswith('?'):
                    new_question += '?'
                new_answer = read_y_n('And what is the answer for a {0}?'.format(new_animal))
                game.update(new_animal, new_question, new_answer.startswith('y'))
                print('Okay, I\'ll know what a {0} is next time!'.format(new_animal))
        else:
            print('Cool, I managed to guess {0} in only {1} questions'.format(game.current_node(), question_count))
        keep_playing = read_y_n('Would you like to play again?')
        game.reset()
        
    print('Okay.. it was fun playing with you!')
