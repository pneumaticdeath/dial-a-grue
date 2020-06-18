# -*- coding: utf-8-*-

import logging
import os
import pty
import re
import time
from client import jasperpath


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
        logger.debug(os.read(fd, 3000))
        exited = False
        while phone.off_hook():
            time.sleep(0.1)
            try:
                stat_pid, status = os.waitpid(pid, os.WNOHANG)
                if stat_pid == pid and os.WIFEXITED(status):
                    exited = True
                    if os.WEXITSTATUS(status) == 0:
                        logger.info('mpg321 exited normally')
                        break
                    else:
                        logger.warn('mpg321 exited with status {}'.format(os.WEXITSTATUS(status)))
            except OSError as e:
                logger.error('Error checking on pid {}: {}'.format(pid, str(e)))
                break
        if not exited:
            logger.debug('Trying to kill pid {}'.format(pid))
            try:
                os.kill(pid, 1)
                wait_pid, status = os.wait()
                if wait_pid == pid:
                    logger.debug('pid {0} exited with status {1}'.format(wait_pid, os.WEXITSTATUS(status)))
                else:
                    logger.warning('wait returned PID {0} when expecting {1} (status {2})'
                                   .format(wait_pid, pid, status))
            except OSError:
                logger.warn('Got error when trying to kill child process')
    else:
        logger.warning('pty.fork returned status {0}'.format(pid))

def isValid(text):
    logger.debug('Heard "{0}"'.format(text))
    return bool(re.search(r'\b(grue|grew)\b', text, re.IGNORECASE))
