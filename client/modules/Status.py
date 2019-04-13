# vim: ai sw=4 expandtab:
import logging
import re
import subprocess

WORDS = [ 'CHECK', 'STATUS'  ]

INSTANCE_WORDS = WORDS

PRIORITY = 101

def handle(text, mic, profile):
    """
    Check the phone status
    """

    def output(string):
        print(string)
        mic.say(string)

    output('Checking phone status')

    status_output = subprocess.check_output('../bin/status')
    for line in status_output.split('\n'):
        output(line)
    logging.info('Done checking phone status')

def isValid(text):
    """
    "Check status"
    """

    return bool(re.search(r'\bstatus\b', text, re.IGNORECASE))
