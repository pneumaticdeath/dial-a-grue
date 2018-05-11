#!/usr/bin/env python
# vim: sw=4 ai expandtab

import jasperpath
import logging
from gpio_switch import Switch
import os
import yaml

class CompoundSwitch(object):
    def __init__(self, pattern, switches):
        self._pattern = pattern
        self._switches = switches

    def is_closed(self):
        for switch, value in self._pattern.items():
            if self._switches[switch].is_closed() != value:
                return False
        return True

touchtone_defs = {
    '1': {'col1':  True, 'col2': False, 'col3': False, 'row1':  True, 'row2': False, 'row3': False, 'row4': False},
    '2': {'col1': False, 'col2':  True, 'col3': False, 'row1':  True, 'row2': False, 'row3': False, 'row4': False},
    '3': {'col1': False, 'col2': False, 'col3':  True, 'row1':  True, 'row2': False, 'row3': False, 'row4': False},
    '4': {'col1':  True, 'col2': False, 'col3': False, 'row1': False, 'row2':  True, 'row3': False, 'row4': False},
    '5': {'col1': False, 'col2':  True, 'col3': False, 'row1': False, 'row2':  True, 'row3': False, 'row4': False},
    '6': {'col1': False, 'col2': False, 'col3':  True, 'row1': False, 'row2':  True, 'row3': False, 'row4': False},
    '7': {'col1':  True, 'col2': False, 'col3': False, 'row1': False, 'row2': False, 'row3':  True, 'row4': False},
    '8': {'col1': False, 'col2':  True, 'col3': False, 'row1': False, 'row2': False, 'row3':  True, 'row4': False},
    '9': {'col1': False, 'col2': False, 'col3':  True, 'row1': False, 'row2': False, 'row3':  True, 'row4': False},
    '*': {'col1':  True, 'col2': False, 'col3': False, 'row1': False, 'row2': False, 'row3': False, 'row4':  True},
    '0': {'col1': False, 'col2':  True, 'col3': False, 'row1': False, 'row2': False, 'row3': False, 'row4':  True},
    '#': {'col1': False, 'col2': False, 'col3':  True, 'row1': False, 'row2': False, 'row3': False, 'row4':  True},
}

class Phone(object):
    _PHONE = None

    @classmethod
    def get_phone(cls):
        if cls._PHONE is None:
            cls._PHONE = cls()

        return cls._PHONE

    def __init__(self, profile=None):
        self._switches = {}
        self._dial_stack = []
        if profile is None:
            profile = jasperpath.config('phone.yml')
        self.load_profile(profile)
        self._monitor()

    def load_profile(self, filename):
        with open(filename, 'r') as f:
            self.profile = yaml.safe_load(f)
        if self.profile['type'] == 'touchtone':
            self._touchtone_init()
        elif self.profile['type'] == 'rotary':
            self._rotary_init()
        deferred_defs = []
        for button in self.profile['buttons']:
            if button not in self.profile:
                logging.error('Button {0} not defined in profile'.format(button))
                continue
            if self.profile[button]['class'] == 'physical':
                self._switches[button] = Switch(self.profile[button]['pin'])
            elif self.profile[button]['class'] == 'alias':
                deferred_defs.append(button)
        for button in deferred_defs:
            self._switches[button] = self._switches[self.profile[button]['alias']]

    def _touchtone_init(self):
        for switch, pin in self.profile['touchtone'].items():
            self._switches[switch] = Switch(pin)
        for button, button_pattern in touchtone_defs.items():
            self._switches[button] = CompoundSwitch(button_pattern, self._switches)
        self._monitor = self._touchtone_monitor

    def _rotary_init(self):
        self._switches['pulse'] = Switch(self.profile['rotary']['pulse'])
        self._monitor = self._rotary_monitor

    def _touchtone_monitor(self):
        pass

    def _rotary_monitor(self):
        pass 

    def off_hook(self):
        return self._switches['hook'].is_closed()

    def on_hook(self):
        return not self.off_hook()

    def ptt_pressed(self):
        return self._switches['ptt'].is_closed()


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
