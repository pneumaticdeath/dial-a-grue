#!/usr/bin/env python

class Phone(object):
    _PHONE = None

    @classmethod
    def get_phone(cls):
        if cls._PHONE is None:
            cls._PHONE = cls()

        return cls._PHONE

    def __init__(self, ptt_pin="XIO-P7", hook_pin="XIO-P6"):
        pass


    def off_hook(self):
        return True

    def on_hook(self):
        return not self.off_hook()

    def ptt_pressed(self):
        return True

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
