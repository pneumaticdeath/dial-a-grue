# -*- coding: utf-8-*-
import logging
import time
# from notifier import Notifier
from brain import Brain
from phone import Phone


class Conversation(object):

    def __init__(self, persona, mic, profile):
        self._logger = logging.getLogger(__name__)
        self.persona = persona
        self.mic = mic
        self.profile = profile
        self.brain = Brain(mic, profile)
        # self.notifier = Notifier(profile)
        self.phone = Phone.get_phone()

    def handleForever(self):
        """
        Delegates user input to the handling function when activated.
        """
        self._logger.info("Starting to handle conversation with keyword '%s'.",
                          self.persona)
        while True:
            while self.phone.on_hook():
                time.sleep(1)

            self.mic.say("How can I be of service? Please hold down the "
                         "PTT button to talk.")

            while self.phone.off_hook():

                if not self.phone.ptt_pressed():
                    time.sleep(0.1)
                    continue

                input = self.mic.activeListenToAllOptions()

                if input:
                    self.brain.query(input)
                else:
                    self.mic.say("Pardon?")
