# vim: ai sw=4 expandtab:
import fcntl
import logging
import os
import pty
import time
from client import jasperpath
# from client.phone import Phone

logger = logging.getLogger(__name__)

class StopGame(Exception):
    pass

class ZorkMachine(object):
  
    def __init__(self, story=None, blocking=False):
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
            return os.read(self._fd, 3000)
        except OSError:
            return ''

    def write(self,str):
        return os.write(self._fd, str)
    
    def kill(self):
        wait_count = 0
        try:
            os.kill(self._pid, 1)
            pid, status = os.waitpid(self._pid, os.WNOHANG)
            while wait_count < 10 and (pid == 0 or not os.WIFEXITED(status)):
                wait_count += 1
                time.sleep(0.1)
                pid, status = os.waitpid(self._pid, os.WNOHANG)
            if pid != 0 and os.WIFEXITED(status):
                logger.debug('zvm with pid {0} exited with status {1}'.format(pid, os.WEXITSTATUS(status)))
            else:
                logger.warn('zvm with pid {0} did not exit'.format(self._pid))
        except OSError as e:
            logger.warn('Got error trying to kill zvm with pid {0}: {1}'.format(self._pid, repr(e)))

    def is_running(self):
        try:
            pid, status = os.waitpid(self._pid, os.WNOHANG)
            if pid != 0 and os.WIFEXITED(status):
                logger.info('zvm with pid {0} exited with status {1}'.format(pid, os.WEXITSTATUS(status)))
                return False
            else:
                return True
        except OSError:
            return False
        return True

class ZorkPhone(object):

    def __init__(self, zvm, mic, munger=None, listen_handlers=[]):
        self.zvm = zvm
        self.mic = mic
        self.munger = munger
        self.listen_handlers = listen_handlers
        self.talker_handler = None
        self.phone = mic.phone
        self.running = True
        self.context = {}
        self.run()

    def run(self):
        time.sleep(0.5)
        try:
            while self.running and self.zvm.is_running():
                logger.debug('Starting talk phase')
                self.talk()
                time.sleep(0.1)
                logger.debug('Starting listen phase')
                self.listen()
                time.sleep(0.1)
        except StopGame as e:
            print('ZorkPhone caught: {}'.format(repr(e)))
        finally:
            self.zvm.kill()

    def listen(self):
        if not self.zvm.is_running():
            raise StopGame()

        player_said = ''
	player_said = self.mic.activeListen()
	if not player_said or player_said == '':
            logger.info('listen got no input')
            return

        for regex, handler in self.listen_handlers:
            match = regex.search(player_said)
            if match:
                logger.debug('handler matched "{0}"'.format(player_said))
                handler(player_said, match, self)

        if self.zvm.is_running():
            if player_said != '':
                logger.debug('player said "{}"'.format(player_said))
		self.zvm.write(player_said + "\n")
        else:
            raise StopGame()

    def talk(self):
        zork_output = ''
        zork_said = ''
        retry_count = 0
        while zork_said == '' and retry_count < 10:
            retry_count += 1
            if self.zvm.is_running():
                logger.debug('Starting to read from zvm')
                zork_said = self.zvm.read()
                logger.debug('got "{}" from zvm'.format(zork_said))
            else:
                raise StopGame()
        if retry_count >= 10:
            logger.debug('Failed to output anything after 10 tries')
            return

        while zork_said and zork_said !='':
            if self.talker_handler is not None:
                zork_said = self.talker_handler(self, zork_said)

            if self.munger is not None:
                zork_said = self.munger(zork_said)

            zork_output += zork_said

            if self.zvm.is_running():
                logger.debug('Starting to read from zvm')
                zork_said = self.zvm.read()
                logger.debug('got "{}" from zvm'.format(zork_said))
            else:
                raise StopGame()

        self.announce(zork_output)

    def announce(self, text):
        print text
        lines = text.split('\n')
        question_last = False
        for line in lines:
            line = line.strip()
            logger.debug('starting processing of line "{}"'.format(line))
            if '?' in line:
                question_last = True
            elif '.' in line or '!' in line:
                question_last = False

            if line == '':
                time.sleep(0.25)
            elif line.endswith('>'):
                if not question_last:
                    if len(line) > 1:
                        self.mic.say(line[:-1].lower())
                    self.mic.say('What would you like to do?')
                return
            else:
                self.mic.say(line.lower())

