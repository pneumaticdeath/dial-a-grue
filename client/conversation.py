# -*- coding: utf-8-*-
import logging
import time
from notifier import Notifier
from brain import Brain
from phone import Phone


class Conversation(object):

    def __init__(self, persona, mic, profile):
        self._logger = logging.getLogger(__name__)
        self.persona = persona
        self.mic = mic
        self.profile = profile
        self.brain = Brain(mic, profile)
        self.notifier = Notifier(profile)
        self.phone = Phone.get_phone()

    def handleForever(self):
        """
        Delegates user input to the handling function when activated.
        """
        self._logger.info("Starting to handle conversation with keyword '%s'.",
                          self.persona)
        while True:
            if self.phone.on_hook():
                time.sleep(0.01)
                continue

            # Print notifications until empty
            notifications = self.notifier.getAllNotifications()
            for notif in notifications:
                self._logger.info("Received notification: '%s'", str(notif))

            if not self.phone.ptt_pressed():
                self._logger.info("PTT button not pressed.")
                time.sleep(0.01)
                continue
                
            input = self.mic.activeListenToAllOptions()

            if input:
                self.brain.query(input)
            else:
                self.mic.say("Pardon?")
