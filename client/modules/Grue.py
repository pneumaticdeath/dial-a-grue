# -*- coding: utf-8-*-

import logging
import os
import re
from client import jasperpath
from client.utils.run_while import run_while


WORDS = ['GRUE']
DIAL_NUMBER = '42'

PRIORITY = 0

logger = logging.getLogger(__name__)

def handle(text, mic, profile):
    # Easter egg
    phone = mic.phone
    mp3file = os.path.join(jasperpath.DATA_PATH, 'pitch_dark.mp3')
    args = ['/usr/bin/mpg321', mp3file]
    run_while(phone.off_hook, args[0], args)

def isValid(text):
    logger.debug('Heard "{0}"'.format(text))
    return bool(re.search(r'\b(grue|grew)\b', text, re.IGNORECASE))
