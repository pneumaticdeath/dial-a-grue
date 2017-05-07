# vim: ai sw=4 expandtab:
import fcntl
import logging
import os
import pty
import re
import threading
import time
from client import jasperpath
from client.phone import Phone

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
    def __init__(self, zvm, mic, copyright_beacon=None):
        self.zvm = zvm
        self.mic = mic
        self.beacon = copyright_beacon
        self.phone = Phone.get_phone()
        self.running = True
        self.listener = threading.Thread(target=self.listen)
        self.talker = threading.Thread(target=self.talk)
        self.quit_said = False
        self.heard_save = False
        self.heard_restore = False
        self.waiting_for_quit_confirmation = False
        self.listener.start()
        self.talker.start()

    def listen(self):
        player_said = ''

        try:
            while self.running and self.zvm.is_running() and self.phone.off_hook():
                if not player_said or player_said == '':
                    logger.info('listen thread got no input')
                    player_said = self.mic.activeListen()
                    continue

                if player_said.upper() == "QUIT":
                    logger.debug('so you want to quit, eh?')
                    self.quit_said = True
                elif player_said.upper() == "SAVE":
                    logger.debug('heard save')
                    self.heard_save = True
                elif player_said.upper() == "RESTORE":
                    logger.debug('heard restore')
                    self.heard_restore = True

                if self.waiting_for_quit_confirmation:
                    logger.debug('listen thread is waiting for quit confirmation')
                    self.waiting_for_quit_confirmation = False
                    if player_said.upper() == "YES":
                        self.mic.say('That was a good game!')
                        self.running = False
                        break

                self.zvm.write(player_said + "\n")

                player_said = self.mic.activeListen()
                logger.debug('listen thread heard "{0}"'.format(player_said))

            if self.zvm.is_running(): 
                try:
                    self.zvm.kill()
                    logger.debug('listen thread killed zvm')
                except Exception as e:
                    logger.debug('listen thread killing zvm caught {0}'.format(str(e)))
        except Exception as e:
            logger.warning('listen thread caught {0}'.format(str(e)))

        self.running = False
        logger.debug('listen thread exiting')

    def talk(self):
        first_block = True
        saved_text = ''
        try:
            while self.running and self.zvm.is_running() and self.phone.off_hook():
                zork_said = saved_text + self.zvm.read()
                if first_block:
                    # print out the copyright notice, but don't speak it since that doesn't work well.
                    if self.beacon is not None:
                        pattern = self.beacon
                    else:
                        pattern = ''
                    ind = zork_said.find(pattern)
                    if ind >= 0:
                        print zork_said[:ind]
                        zork_said = zork_said[ind:]
                        first_block = False
                        saved_text = ''
                    else:
                        saved_text = zork_said
                        continue

                if self.quit_said:
                    quit_sub = 'Do you wish to leave the game? (Y is affirmative): >'
                    quit_repl = 'Do you wish to leave the game?'
                    ind = zork_said.find(quit_sub)
                    if ind >= 0:
                        zork_said = zork_said[:ind] + quit_repl + zork_said[ind + len(quit_sub):]
                        self.quit_said = False
                        self.waiting_for_quit_confirmation = True
                elif self.heard_save or self.heard_restore:
                    pattern = 'Enter a file name.'
                    if pattern in zork_said:
                        if self.heard_save:
                            self.announce('Saving')
                            self.heard_save = False
                        if self.heard_restore:
                            self.announce('Loading')
                            self.heard_restore = False
                        # save/load from default filename
                        self.zvm.write('\n')
                        time.sleep(0.1)
                        zork_said = self.zvm.read()
                        if 'Y/N' in zork_said:
                            self.zvm.write('y\n')
                            zork_said = 'Overwrote old save'

                self.announce(zork_said)
            if self.zvm.is_running():
                try:
                    self.zvm.kill()
                    logger.debug('talk thread killed zvm')
                except Exception as e:
                    logger.debug('talk thread killing zvm caught {0}'.format(str(e)))
        except Exception as e:
            logger.warning('talk thread caught {0}'.format(str(e)))

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

