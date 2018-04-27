#!/usr/bin/python
# vim: sw=4 ai expandtab

import atexit
import os
import time

if 'ntc' in os.uname()[2]:
    from CHIP_IO import GPIO
else:
    from RPi import GPIO
    GPIO.setmode(GPIO.BCM)

atexit.register(GPIO.cleanup)

class Switch(object):

    def __init__(self, pin, debounce_threshold=0.02):
        self.pin = pin
        self.debounce = debounce_threshold

        try:
            # TODO(mitch): figure out why this throws exceptions sometimes
            GPIO.setup(self.pin, GPIO.IN, GPIO.PUD_UP)
        except Exception as e:
            print "Got exception %s when trying to initialize %s" % (str(e), self.pin)
            pass

        self._value = self._read()
        self._last_xition_time = time.time()

    def _read(self):
        return GPIO.input(self.pin)

    def is_closed(self):
        if (time.time() - self._last_xition_time) >= self.debounce:
            new_val = self._read()
            if self._value != new_val:
                self._value = new_val
                self._last_xition_time = time.time()

        return not self._value

