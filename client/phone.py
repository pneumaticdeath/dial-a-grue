#!/usr/bin/env python

from gpio_switch import Switch

class Phone(object):
    _PHONE = None

    @classmethod
    def get_phone(cls):
        if cls._PHONE is None:
            cls._PHONE = cls()

        return cls._PHONE

    def __init__(self, ptt_pin="XIO-P5", hook_pin="XIO-P4"):
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
