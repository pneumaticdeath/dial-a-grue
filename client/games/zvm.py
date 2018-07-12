# vim: ai sw=4 expandtab:
import fcntl
import logging
import os
import pty
import threading
import time
from client import jasperpath
# from client.phone import Phone

logger = logging.getLogger(__name__)

class ZorkMachine(object):
  
    def __init__(self, story=None, blocking=True):
        self._pid,self._fd = pty.fork()
        if self._pid == 0:
            # We need to exec the zvm, and it needs to run in its own dir
            os.chdir(os.path.join(jasperpath.APP_PATH, 'static', 'zvm'))
            args = ['./zvm',]
            if story is not None:
                args.append(story)
            os.execv('./zvm', args)
        else:
            if not blocking:
                flags = fcntl.fcntl(self._fd, fcntl.F_GETFL)
                fcntl.fcntl(self._fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
            print "Forked zvm in PID %d" % (self._pid,)


    def read(self):
        try:
            return os.read(self._fd, 30000)
        except OSError:
            return ''

    def write(self,str):
        return os.write(self._fd, str)
    
    def kill(self):
        os.kill(self._pid, 1)
        pid, status = os.waitpid(self._pid, os.WNOHANG)
        logging.debug('zvm with pid {0} exited with status {1}'.format(pid, status))

    def is_running(self):
        try:
            os.kill(self._pid, 0)
        except OSError:
            return False
        return True

class ZorkPhone(object):

    class StopGame(Exception):
        pass

    def __init__(self, zvm, mic, munger=None, listen_handlers=[]):
        self.zvm = zvm
        self.mic = mic
        self.munger = munger
        self.listen_handlers = listen_handlers
        self.talker_handler = None
        self.phone = mic.phone
        self.running = True
        self.context = {}
        self.listener = threading.Thread(target=self.listen)
        self.talker = threading.Thread(target=self.talk)
        self.listener.start()
        self.talker.start()

    def listen(self):
        player_said = ''

        try:
            while self.running and self.zvm.is_running() and self.phone.off_hook():
                player_said = self.mic.activeListen()
                if not player_said or player_said == '':
                    logger.info('listen thread got no input')
                    continue

                for regex, handler in self.listen_handlers:
                    match = regex.search(player_said)
                    if match:
                        logging.debug('handler matched "{0}"'.format(player_said))
                        handler(player_said, match, self)

                self.zvm.write(player_said + "\n")


            if self.zvm.is_running(): 
                try:
                    self.zvm.kill()
                    logger.debug('listen thread killed zvm')
                except Exception as e:
                    logger.debug('listen thread killing zvm caught {0}'.format(repr(e)))
        except Exception as e:
            logger.warning('listen thread caught {0}'.format(repr(e)))

        self.running = False
        logger.debug('listen thread exiting')

    def talk(self):
        try:
            while self.running and self.zvm.is_running() and self.phone.off_hook():
                zork_said = self.zvm.read()
                if self.talker_handler is not None:
                    zork_said = self.talker_handler(self, zork_said)
                    self.talker_handler = None

                if self.munger is not None:
                    zork_said = self.munger(zork_said)

                self.announce(zork_said)
            if self.zvm.is_running():
                try:
                    self.zvm.kill()
                    logger.debug('talk thread killed zvm')
                except Exception as e:
                    logger.debug('talk thread killing zvm caught {0}'.format(repr(e)))
        except Exception as e:
            logger.warning('talk thread caught {0}'.format(repr(e)))

        self.running = False
        logger.debug('talk thread exiting')

    def announce(self, text):
        print text
        lines = text.split('\n')
        question_last = False
        for line in lines:
            if self.phone.ptt_pressed():
                break
            line = line.strip()
            if line.endswith('?'):
                question_last = True
            elif line.endswith('.') or line.endswith('!'):
                question_last = False

            if line == '':
                time.sleep(0.25)
            elif line == '>':
                if not question_last:
                    self.mic.say('What would you like to do?')
                return
            else:
                self.mic.say(line.lower())

