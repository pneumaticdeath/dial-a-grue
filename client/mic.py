# -*- coding: utf-8-*-
"""
    The Mic class handles all interactions with the microphone and speaker.
"""
import logging
import tempfile
import wave
import audioop
import pyaudio
import alteration
import jasperpath
import os
import subprocess
import threading
import time

import phone
# import local_phone as phone


class Mic:

    speechRec = None
    speechRec_persona = None

    def __init__(self, speaker, passive_stt_engine, active_stt_engine):
        """
        Initiates the pocketsphinx instance.

        Arguments:
        speaker -- handles platform-independent audio output
        passive_stt_engine -- performs STT while Jasper is in passive listen
                              mode
        acive_stt_engine -- performs STT while Jasper is in active listen mode
        """
        self._logger = logging.getLogger(__name__)
        self.lock = threading.Lock()
        self.speaker = speaker
        self.passive_stt_engine = passive_stt_engine
        self.active_stt_engine = active_stt_engine
        self.phone = phone.get_phone()
        self._logger.info("Initializing PyAudio. ALSA/Jack error messages " +
                          "that pop up during this process are normal and " +
                          "can usually be safely ignored.")
        self._audio = pyaudio.PyAudio()
        self._logger.info("Initialization of PyAudio completed.")
        self._echo = False  # whether to play back what it heard

    def __del__(self):
        self._audio.terminate()

    def getScore(self, data):
        rms = audioop.rms(data, 2)
        score = rms / 3
        return score

    def fetchThreshold(self):

        # TODO: Consolidate variables from the next three functions
        THRESHOLD_MULTIPLIER = 1.8
        # RATE = 16000
        RATE = 44100
        # RATE = 8000
        # CHUNK = 1024
        CHUNK = 32

        # number of seconds to allow to establish threshold
        THRESHOLD_TIME = 1

        # prepare recording stream
        stream = self._audio.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=RATE,
                                  input=True,
                                  input_device_index=1,
                                  frames_per_buffer=CHUNK)

        # stores the audio data
        frames = []

        # stores the lastN score values
        lastN = [i for i in range(int(20480/CHUNK))]

        # calculate the long run average, and thereby the proper threshold
        for i in range(0, int(RATE / CHUNK * THRESHOLD_TIME + 0.5)):

            data = stream.read(CHUNK, False)
            frames.append(data)

            # save this data point as a score
            lastN.pop(0)
            lastN.append(self.getScore(data))
            average = sum(lastN) / len(lastN)

        stream.stop_stream()
        stream.close()

        # this will be the benchmark to cause a disturbance over!
        THRESHOLD = average * THRESHOLD_MULTIPLIER

        return THRESHOLD

    def passiveListen(self, PERSONA):
        """
        Listens for PERSONA in everyday sound. Times out after LISTEN_TIME, so
        needs to be restarted.
        """

        THRESHOLD_MULTIPLIER = 1.8
        RATE = 44100
        CHUNK = 32

        # number of seconds to allow to establish threshold
        THRESHOLD_TIME = 1

        # number of seconds to listen before forcing restart
        LISTEN_TIME = 10

        # prepare recording stream
        stream = self._audio.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=RATE,
                                  input=True,
                                  input_device_index=1,
                                  frames_per_buffer=CHUNK)

        # stores the audio data
        frames = []

        # stores the lastN score values
        lastN = [i for i in range(int(30720/CHUNK))]

        # calculate the long run average, and thereby the proper threshold
        for i in range(0, RATE / CHUNK * THRESHOLD_TIME):

            data = stream.read(CHUNK)
            frames.append(data)

            # save this data point as a score
            lastN.pop(0)
            lastN.append(self.getScore(data))
            average = sum(lastN) / len(lastN)

        # this will be the benchmark to cause a disturbance over!
        THRESHOLD = average * THRESHOLD_MULTIPLIER

        # save some memory for sound data
        frames = []

        # flag raised when sound disturbance detected
        didDetect = False

        # start passively listening for disturbance above threshold
        for i in range(0, RATE / CHUNK * LISTEN_TIME):

            data = stream.read(CHUNK)
            frames.append(data)
            score = self.getScore(data)

            if score > THRESHOLD:
                didDetect = True
                break

        # no use continuing if no flag raised
        if not didDetect:
            print "No disturbance detected"
            stream.stop_stream()
            stream.close()
            return (None, None)

        # cutoff any recording before this disturbance was detected
        frames = frames[-int(20480/CHUNK):]

        # otherwise, let's keep recording for few seconds and save the file
        DELAY_MULTIPLIER = 1
        for i in range(0, RATE / CHUNK * DELAY_MULTIPLIER):

            data = stream.read(CHUNK)
            frames.append(data)

        # save the audio data
        stream.stop_stream()
        stream.close()

        with tempfile.NamedTemporaryFile(mode='w+b') as f:
            wav_fp = wave.open(f, 'wb')
            wav_fp.setnchannels(1)
            wav_fp.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
            wav_fp.setframerate(RATE)
            wav_fp.writeframes(''.join(frames))
            wav_fp.close()
            f.seek(0)
            # check if PERSONA was said
            transcribed = self.passive_stt_engine.transcribe(f)

        if any(PERSONA in phrase for phrase in transcribed):
            return (THRESHOLD, PERSONA)

        return (False, transcribed)

    def activeListen(self, THRESHOLD=None, LISTEN=True, MUSIC=False):
        """
            Records until a second of silence or times out after 12 seconds

            Returns the first matching string or None
        """

        options = self.activeListenToAllOptions(THRESHOLD, LISTEN, MUSIC)
        if options:
            return options[0]

    def activeListenToAllOptions(self, THRESHOLD=None, LISTEN=True,
                                 MUSIC=False):
        """
            Records until a second of silence or times out after 12 seconds

            Returns a list of the matching options or None
        """

        TARGET_RATE = 16000
        RATE = 44100
        # CHUNK = 1024
        CHUNK = 32
        LISTEN_TIME = 12

        # check if no threshold provided
        if THRESHOLD is None:
            THRESHOLD = self.fetchThreshold()

        wait_count = 0
        while not self.phone.ptt_pressed() and wait_count < 120:
            wait_count += 1
            time.sleep(0.1)
            if self.phone.on_hook():
                raise phone.Hangup

        if not self.phone.ptt_pressed():
            return ['',]

        self.lock.acquire()

        self.speaker.play(jasperpath.data('audio', 'beep_hi.wav'))

        # prepare recording stream
        stream = self._audio.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=RATE,
                                  input=True,
                                  input_device_index=1,
                                  frames_per_buffer=CHUNK)

        frames = []
        # increasing the range # results in longer pause after command
        # generation
        lastN = [THRESHOLD * 1.2 for i in range(int(30720/CHUNK))]

        for i in range(0, RATE / CHUNK * LISTEN_TIME):

            data = stream.read(CHUNK, False)
            frames.append(data)
            score = self.getScore(data)

            lastN.pop(0)
            lastN.append(score)

            average = sum(lastN) / float(len(lastN))

            # TODO: 0.8 should not be a MAGIC NUMBER!
            # if average < THRESHOLD * 0.8:
            if not self.phone.ptt_pressed() and average < THRESHOLD * 0.8:
                break

        self.speaker.play(jasperpath.data('audio', 'beep_lo.wav'))

        # save the audio data
        stream.stop_stream()
        stream.close()

        self.lock.release()

        with tempfile.NamedTemporaryFile(mode='w+b', suffix='.wav', delete=True) as f:
            wav_fp = wave.open(f, 'wb')
            wav_fp.setnchannels(1)
            wav_fp.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
            wav_fp.setframerate(RATE)
            wav_fp.writeframes(''.join(frames))
            wav_fp.close()
            f.seek(0)
            if RATE == TARGET_RATE:
                candidates = self.active_stt_engine.transcribe(f)
                if self._echo:
                    self.speaker.play(f.name)
            else:
                resampled_file = resample(f.name, TARGET_RATE)
                f_prime = open(resampled_file)
                candidates = self.active_stt_engine.transcribe(f_prime)
                f_prime.close()
                if self._echo:
                    self.speaker.play(resampled_file)
                os.remove(resampled_file)

            if candidates:
                self._logger.info('Got the following possible transcriptions:')
                for c in candidates:
                    self._logger.info(c)
            # f.close()
            return candidates

    def say(self, phrase,
            OPTIONS=" -vdefault+m3 -p 40 -s 160 --stdout > say.wav"):
        # alter phrase before speaking
        phrase = alteration.clean(phrase)
        self.lock.acquire()
        self.speaker.say(phrase)
        self.lock.release()

def resample(filename, rate):
    ofd, ofn = tempfile.mkstemp(suffix='.wav')
    os.close(ofd)
    cmd = ['sox', filename, ofn, 'rate', str(rate)]
    with tempfile.TemporaryFile() as f:
        subprocess.call(cmd, stdout=f, stderr=f)
        f.seek(0)
        output=f.read()
        if output:
            logging.debug('Output of resample was: {0}'.format(output))
    return ofn
