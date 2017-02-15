#!/usr/bin/env python

from gpio_switch import Switch

class Phone(object):
    _PHONE = None

    @classmethod
    def get_phone(cls):
        if cls._PHONE is None:
            cls._PHONE = cls()

        return cls._PHONE

    def __init__(self, ptt_pin="XIO-P7", hook_pin="XIO-P6"):
        self._ptt = Switch(ptt_pin)
        self._hook = Switch(hook_pin)


    def off_hook(self):
        return self._hook.is_closed()

    def on_hook(self):
        return not self.off_hook()

    def ptt_pressed(self):
        return self._ptt.is_closed()
