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

class AbstractSwitch(object):
    def __init__(self, debounce_threshold=0.02):
        self._debounce = debounce_threshold
        self._onclose_cb = []
        self._onopen_cb = []
        self._last_xition_time = time.time()
        self._interval = 0
        self._value = self._read()

    def _read(self):
        return False

    def on_close(self, func):
        self._onclose_cb.append(func)

    def on_open(self, func):
        self._onopen_cb.append(func)

    def is_closed(self):
        if (time.time() - self._last_xition_time) >= self._debounce:
            new_value = self._read()
            if self._value != new_value:
                self._interval = time.time() - self._last_xition_time
                self._last_xition_time = time.time()
                self._value = new_value
                if self._value:
                    for cb in self._onopen_cb:
                        cb(not self._value, self._interval)
                else:
                    for cb in self._onclose_cb:
                        cb(not self._value, self._interval)

        return not self._value

class Switch(AbstractSwitch):

    def __init__(self, pin, *args,**kwargs):
        self.pin = pin
        try:
            # TODO(mitch): figure out why this throws exceptions sometimes
            GPIO.setup(self.pin, GPIO.IN, GPIO.PUD_UP)
        except Exception as e:
            print("Got exception {} when trying to initialize {}".format(str(e), self.pin))
            pass
        super(Switch, self).__init__(*args,**kwargs)

    def _read(self):
        return GPIO.input(self.pin)

class CompoundSwitch(AbstractSwitch):
    def __init__(self, pattern, switches, *args, **kwargs):
        self._pattern = pattern
        self._switches = switches
        super(CompoundSwitch, self).__init__(*args, **kwargs)

    def _read(self):
        for switch, value in self._pattern.items():
            if self._switches[switch].is_closed() != value:
                return True #inverse logic
        return False
