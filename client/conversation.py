# -*- coding: utf-8-*-
import logging
import time
# from notifier import Notifier
from brain import Brain
import phone


class Conversation(object):

    def __init__(self, persona, mic, profile, active_stt_engine=None):
        self._logger = logging.getLogger(__name__)
        self.persona = persona
        self.mic = mic
        self.profile = profile
        self.brain = Brain(mic, profile, active_stt_engine, echo=mic._echo)
        # self.notifier = Notifier(profile)
        self.phone = mic.phone

    def handleForever(self):
        """
        Delegates user input to the handling function when activated.
        """

        greeting = self.profile['greeting']
        self._logger.info("Starting to handle conversation")
        while True:
            while self.phone.on_hook():
                time.sleep(1)

            try:
                while self.phone.off_hook():
                    time.sleep(1)
                    # self.phone.dial_stack() # clear dial stack
                    print('Welcome grue fodder!')
                    self.mic.say(greeting)
                    input = self.mic.activeListenToAllOptions()
                    dialed_number = ''.join(self.mic.dial_stack())

                    if dialed_number != "":
                        self.brain.dial(dialed_number, input)
                    elif input:
                        self.brain.query(input)
                    else:
                        self.mic.say("Pardon?")

            except phone.Hangup:
                print('Got HUP')

