# -*- coding: utf-8-*-

import logging
import os
import pty
import re
import time
from client import jasperpath
from client.phone import Phone


WORDS = ['GRUE']

PRIORITY = 0

logger = logging.getLogger(__name__)

def handle(text, mic, profile):
    # Easter egg
    phone = mic.phone
    mp3file = os.path.join(jasperpath.DATA_PATH, 'pitch_dark.mp3')
    pid, fd = pty.fork()
    if pid == 0:
        args = ['/usr/bin/mpg321', mp3file]
        time.sleep(0.5)
        os.execv(args[0], args)
    elif pid > 0:
        logging.info('Forked pid {0}'.format(pid))
        try:
            logger.debug(os.read(fd, 3000))
            while phone.off_hook() and not phone.ptt_pressed():
                time.sleep(0.1)
                os.kill(pid, 0)
            logger.debug('phone hung up')
            os.kill(pid, 1)
        except OSError:
            logger.debug('mpg321 exited naturally')
        wait_pid, status = os.wait()
        if wait_pid == pid:
            logger.debug('pid {0} exited with status {1}'.format(wait_pid, status))
        else:
            logger.warning('wait returned PID {0} when expecting {1} (status {2})'
                           .format(wait_pid, pid, status))
    else:
        logger.warning('pty.fork returned status {0}'.format(pid))

def isValid(text):
    logger.debug('Heard "{0}"'.format(text))
    return bool(re.search(r'\b(grue|grew)\b', text, re.IGNORECASE))
