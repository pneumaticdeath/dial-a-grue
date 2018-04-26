#!/usr/bin/env python
# vim: sw=4 ai expandtab
# utility functions
# Copyright 2018, Mitch Patenaude

def mk_print_list(l, conjunction='and'):
    '''Makes a list of elements with of the form "a, b, c <conjucntion> d"'''

    if len(l) == 0:
        return ''
    if len(l) == 1:
        return str(l[0])
    else:
        return '{0} {1} {2}'.format(', '.join([str(w) for w in l[:-1]]), conjunction, l[-1])

