# -*- coding: utf-8-*-

import logging
import re
import sys


WORDS = ['NUKE', 'GRUE']

PRIORITY = 0

logger = logging.getLogger(__name__)

def handle(text, mic, profile):
    """
        Exit from the interpreter

    """

    mic.say('I regret that I have but one life to give!')
    sys.exit()


def isValid(text):
    logger.debug('Heard "{0}"'.format(text))
    return bool(re.search(r'\bnuke (grue|grew)\b', text, re.IGNORECASE))
