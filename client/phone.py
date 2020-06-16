#!/usr/bin/env python
# vim: sw=4 ai expandtab

from gpio_switch import Switch, CompoundSwitch
import jasperpath
import logging
import threading
import time
import yaml

_touchtone_defs = {
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

_rotary_map = { 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: '0' }

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
        self._logger = logging.getLogger(__name__)
        if profile is None:
            profile = jasperpath.config('phone.yml')
        self.load_profile(profile)
        self._monitor_thread = threading.Thread(target=self._monitor)
        self._monitor_thread.setDaemon(True)
        self._monitor_thread.setName('phone dial monitor')
        self._monitor_thread.start()

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
                self._logger.error('Button {0} not defined in profile'.format(button))
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
        for button, button_pattern in _touchtone_defs.items():
            def on_close(is_closed, interval, switch=button):
                # the third argument with the default value is a bit of a hack
                # to make a copy of current value of 'button' at def time.
                self._logger.info('{} button pressed'.format(switch))
            def on_open(is_closed, interval, switch=button):
                # the third argument with the default value is a bit of a hack
                # to make a copy of current value of 'button' at def time.
                self._logger.info('{} button released after {} seconds'.format(switch, interval))
                self._dial_stack.append(switch)
            self._switches[button] = CompoundSwitch(button_pattern, self._switches)
            self._switches[button].on_open(on_open)
            self._switches[button].on_close(on_close)
        self._monitor = self._touchtone_monitor

    def _touchtone_monitor(self):
        while True:
            for button in _touchtone_defs.keys():
                self._switches[button].is_closed()
            time.sleep(0.01)

    def _rotary_init(self):
        self._pulse_counter = 0
        self._last_pulse_time = time.time()

        def catch_pulse_start(is_closed, interval):
            pulse_interval = time.time()-self._last_pulse_time
            if pulse_interval <= 0.12 and pulse_interval >= 0.08:
                self._pulse_counter += 1
            elif pulse_interval < 0.08:
                self._logger.warn('Got too short rotary pulse of {} seconds'.format(pulse_interval))
            else:
                if self._pulse_counter > 0:
                    # edge case where the monitor didn't catch the interval
                    self._logger.debug('Last ditch effort to count pulses')
                    self._interpret_pulses()
                self._pulse_counter = 1
            self._last_pulse_time = time.time()

        self._switches['pulse'] = Switch(self.profile['rotary']['pulse'])
        self._switches['pulse'].on_close(catch_pulse_start)
        self._monitor = self._rotary_monitor

    def _rotary_monitor(self):
        while True:
            time.sleep(0.01)
            self._switches['pulse'].is_closed()
            if time.time()-self._last_pulse_time >= 0.15 and self._pulse_counter > 0:
                self._logger.debug('Counting pulses')
                self._interpret_pulses()

    def _interpret_pulses(self):
        if self._pulse_counter in _rotary_map:
            self._dial_stack.append(_rotary_map[self._pulse_counter])
            self._logger.debug('Counted {0} pulses yielding a {1}'.format(self._pulse_counter, _rotary_map[self._pulse_counter]))
        elif self._pulse_counter == 0:
            self._logger.warn('Tried to interpret no pulses')
        else:
            self._logger.error('Got too many pulses: {}'.format(self.pulse_counter))
        self._pulse_counter = 0

    def dial_stack(self):
        stack = self._dial_stack
        self._dial_stack = []
        return stack

    def off_hook(self):
        return self._switches['hook'].is_closed()

    def on_hook(self):
        return not self.off_hook()

    def pressed(self, switch):
        return self._switches[switch].is_closed() if switch in self._switches else False

    def ptt_pressed(self):
        return self.pressed('ptt')


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

    for name, sw in phone._switches.items():
        print('{0} is {1}'.format(name, 'closed' if sw.is_closed() else 'open'))

    while True:
        stack = phone.dial_stack()
        if stack:
            print('Dialed: {}'.format(', '.join(stack)))
        time.sleep(0.5)
