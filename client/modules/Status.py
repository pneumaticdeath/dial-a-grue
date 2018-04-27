# vim: ai sw=4 expandtab:
import logging
import re
import subprocess

WORDS = [ 'CHECK', 'STATUS'  ]

INSTANCE_WORDS = WORDS

PRIORITY = 101

def handle(text, mic, profile):
    """
    Check the battery status
    """

    def output(string):
        print(string)
        mic.say(string)

    output('Checking phone status')

    status_output = subprocess.check_output('/usr/bin/battery.sh')
    status = {}
    for kvp in status_output.split('\n'):
        if kvp.strip():
            key, value = [s.strip() for s in kvp.split('=')]
            # print('{0}={1}'.format(key,value))
            status[key] = value

    if status.get('BAT_EXIST') == '1':
        if status['CHARG_IND'] == '1':
            charge_current = re.sub('mA$', ' mili-amps', status['Battery charge current'])
            output('Battery is charging at {0}'.format(charge_current))
        else:
            discharge_current = re.sub('mA$', ' mili-amps', status['Battery discharge current'])
            output('Battery is discharging at {0}'.format(discharge_current))
        voltage = re.sub('mV$', ' mili-volts', status['Battery voltage'])
        output('Battery voltage is {0}'.format(voltage))
    else:
        output('Battery not present.')

    temp = re.sub('c$', ' degrees celsius', status['Internal temperature'])
    output('Temperature is {0}.'.format(temp))

    logging.info('Done checking batter status')

def isValid(text):
    """
    "Check status"
    """

    return bool(re.search(r'\bstatus\b', text, re.IGNORECASE))
