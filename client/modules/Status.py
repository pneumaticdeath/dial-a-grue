# vim: ai sw=4 expandtab:
from client.games.utils import mk_print_list
import collections
import logging
import re
import subprocess
import threading

WORDS = [ 'CHECK', 'STATUS', 'THREADS'  ]

INSTANCE_WORDS = WORDS

PRIORITY = 99

def handle(text, mic, profile):
    """
    Check the phone status
    """

    def output(string):
        print(string)
        mic.say(string)

    output('Checking phone status')

    threads = threading.enumerate()
    if bool(re.search(r'\bthreads\b', text, re.IGNORECASE)):
        counter = collections.Counter()
        for t in threads:
            counter[t.name] += 1
        for name, count in counter.items():
            output('{0} thread{1} named {2}'.format(count, "s" if count != 1 else "", name))
    else:
        thread_count = len(threads)
        output('{0} thread{1} running'.format(thread_count, "s" if thread_count != 1 else ""))

    output('noise threshold is {0}'.format(int(mic.fetchThreshold())))
    dial_stack = mic.phone.dial_stack()
    if dial_stack:
        output('Dial stack is {}'.format(mk_print_list(dial_stack)))

    status_output = subprocess.check_output('../bin/status')
    for line in status_output.split('\n'):
        output(line)
    logging.info('Done checking phone status')

def isValid(text):
    """
    "Check status"
    """

    return bool(re.search(r'\bstatus\b', text, re.IGNORECASE))
