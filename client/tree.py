#!/usr/bin/env python
# vim: sw=4 ai expandtab

import logging
import sqlite3
import sys
from animal import Node

class Tree(object):
    def __init__(self, db):
        if type(db) is str:
            self._conn = sqlite3.connect(db)
        else:
            self._conn = db

    def printLeaves(self, verbose=False):
        nodes = []
        nodes.append((1, [], Node.find(1, self._conn)))
        while len(nodes) > 0:
            depth, seq, node = nodes[0]
            nodes = nodes[1:]
            if node.yes_node:
                if verbose:
                    nodes.append((depth+1, seq + ['%s%s: yes' % (' ' * depth, node.node_text)], Node.find(node.yes_node, self._conn)))
                    nodes.append((depth+1, seq + ['%s%s: no' % (' ' * depth, node.node_text)], Node.find(node.no_node, self._conn)))
                else:
                    nodes.append((depth+1, seq + ['yes'], Node.find(node.yes_node, self._conn)))
                    nodes.append((depth+1, seq + ['no'], Node.find(node.no_node, self._conn)))
            else:
                if verbose:
                    print("{0}\n{1}-> {2}\n".format('\n'.join(seq), ' ' * depth, node.node_text))
                else:
                    print("{0} {1} {2}".format(depth, ','.join(seq), node.node_text))

    def search(self, name):
        nodes = []
        nodes.append((1, [], Node.find(1, self._conn)))
        while len(nodes) > 0:
            depth, seq, node = nodes[0]
            nodes = nodes[1:]
            if node.yes_node:
                nodes.append((depth+1, seq + [('yes',node)], Node.find(node.yes_node, self._conn)))
                nodes.append((depth+1, seq + [('no',node)], Node.find(node.no_node, self._conn)))
            elif node.node_text.lower().strip() == name.lower().strip():
                return node.node_text, seq
        return None



if __name__ == '__main__':
    def usage():
        print('{0} [-v|--verbose] dbfile [node]')
        sys.exit(1)

    verbose = False
    args = sys.argv[1:]
    if len(args) == 0:
        usage()

    if args[0] in ['-v', '--verbose']:
        verbose = True
        args = args[1:]

    if len(args) == 0:
        usage()

    tree = Tree(args[0])
    if len(args) == 1:
        tree.printLeaves(verbose)
    elif len(args) == 2:
        result = tree.search(args[1])
        if result:
            print('{0}'.format(result[0]))
            depth = 1
            for answer, node in result[1]:
                print('{0}{1}: {2}'.format(' '*depth, node.node_text, answer))
                depth += 1
        else:
            print('Nothing found')

