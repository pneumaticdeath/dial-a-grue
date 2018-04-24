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
        self.brain = Brain(mic, profile, active_stt_engine)
        # self.notifier = Notifier(profile)
        self.phone = mic.phone

    def handleForever(self):
        """
        Delegates user input to the handling function when activated.
        """
        self._logger.info("Starting to handle conversation with keyword '%s'.",
                          self.persona)
        while True:
            while self.phone.on_hook():
                time.sleep(1)

            try:
                self.mic.say("How can I be of service? Please hold down the "
                             "PTT button to talk.")
            except phone.Hangup:
                print('Got HUP')

            while self.phone.off_hook():

                if not self.phone.ptt_pressed():
                    time.sleep(0.1)
                    continue

                try:
                    input = self.mic.activeListenToAllOptions()
                except phone.Hangup:
                    print('Got HUP')

                if input:
                    self.brain.query(input)
                else:
                    self.mic.say("Pardon?")
