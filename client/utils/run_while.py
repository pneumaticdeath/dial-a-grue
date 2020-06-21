import os
import logging
import pty
import time

logger = logging.getLogger(__name__)

def run_while(cond, cmd, args):
    exited = False
    pid = None

    try:
        pid, fd = pty.fork()
        if pid == 0:
            time.sleep(0.1)
            os.execv(cmd, args)
        elif pid < 0:
            logger.warning('pty.fork() returned status {0}'.format(pid))
        else:
            logger.info('Ran cmd "{0}" in pid {1}'.format(' '.join(args), pid))
            logger.debug(os.read(fd, 10240))
            while cond():
                time.sleep(0.1)
                stat_pid, status = os.waitpid(pid, os.WNOHANG)
                if stat_pid == pid and os.WIFEXITED(status):
                    exited = True
                    if os.WEXITSTATUS(status) == 0:
                        logger.info('{0} exited nomally.'.format(cmd))
                    else:
                        logger.warning('pid {0} with cmd {1} and args "{2}" exited with status {3}.' 
                                       .format(stat_pid, cmd, ' '.join(args), os.WEXITSTATUS(status)))
                    pid = None
                    break
            if not cond():
                logger.debug('Fell out of loop because condition no longer met')
                
            if pid is not None and not exited:
                logger.debug('Trying to kill pid {0}'.format(pid))
                os.kill(pid, 1)
                wait_pid, status = os.wait()
                if wait_pid == pid:
                    logger.debug('pid {0} exited with status {1}'.format(wait_pid, os.WEXITSTATUS(status)))
                else:
                    logger.warning('Wait returned pid {0} when expecting {1} (status {2})'
                                   .format(wait_pid, pid, status))
    except OSError as e:
        logger.warning('Got OSError "{0}"'.format(str(e)))

