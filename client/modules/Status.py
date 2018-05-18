# vim: ai sw=4 expandtab:
import logging
import os
import re
import subprocess

WORDS = [ 'CHECK', 'STATUS'  ]

INSTANCE_WORDS = WORDS

PRIORITY = 101

def handle(text, mic, profile):
    """
    Check the battery status
    """

    def output(string):
        print(string)
        mic.say(string)

    output('Checking phone status')

    status_output = subprocess.check_output('../bin/status')
    for line in status_output.split('\n'):
        output(line)
    logging.info('Done checking batter status')

def isValid(text):
    """
    "Check status"
    """

    return bool(re.search(r'\bstatus\b', text, re.IGNORECASE))
