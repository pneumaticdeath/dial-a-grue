#!/usr/bin/env python
# vim: sw=4 ai expandtab

from gpio_switch import Switch
import os

if 'ntc' in os.uname()[2]:
    PTT_PIN='XIO-P5'
    HOOK_PIN='XIO-P4'
else:
    PTT_PIN=22
    HOOK_PIN=23

class Phone(object):
    _PHONE = None

    @classmethod
    def get_phone(cls):
        if cls._PHONE is None:
            cls._PHONE = cls()

        return cls._PHONE

    def __init__(self, ptt_pin=PTT_PIN, hook_pin=HOOK_PIN):
        self._ptt = Switch(ptt_pin)
        self._hook = Switch(hook_pin)


    def off_hook(self):
        return self._hook.is_closed()

    def on_hook(self):
        return not self.off_hook()

    def ptt_pressed(self):
        return self._ptt.is_closed()

class Hangup(Exception):
    pass

def get_phone():
    return Phone.get_phone()

if __name__ == '__main__':
    phone = Phone.get_phone()
    if phone.off_hook():
        print('The phone is off hook')
    else:
        print('The phone is on hook')

    if phone.ptt_pressed():
        print('PTT pressed')
    else:
        print('PTT not pressed')
