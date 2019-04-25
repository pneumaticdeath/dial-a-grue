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
import yaml

import phone
# import local_phone as phone


class Mic:

    speechRec = None
    speechRec_persona = None
    speaker = None
    _last_threshold = None
    _last_threshold_time = None
    _background_threshold_thread = None
    lock = threading.Lock()

    def __init__(self, speaker, passive_stt_engine, active_stt_engine, echo=False):
        """
        Initiates the pocketsphinx instance.

        Arguments:
        speaker -- handles platform-independent audio output
        passive_stt_engine -- performs STT while Jasper is in passive listen
                              mode
        acive_stt_engine -- performs STT while Jasper is in active listen mode
        """
        self._logger = logging.getLogger(__name__)
        self.setSpeaker(speaker)
        self.passive_stt_engine = passive_stt_engine
        self.active_stt_engine = active_stt_engine
        self.phone = phone.get_phone()
        self._logger.info("Initializing PyAudio. ALSA/Jack error messages " +
                          "that pop up during this process are normal and " +
                          "can usually be safely ignored.")
        self._audio = pyaudio.PyAudio()
        self._logger.info("Initialization of PyAudio completed.")
        self._echo = echo # whether to play back what it heard

        self._audio_dev = None
        profile_path = jasperpath.config('profile.yml')
        if os.path.exists(profile_path):
            with open(profile_path, 'r') as f:
                profile = yaml.safe_load(f)
                if 'audio_dev' in profile and 'speaker' in profile['audio_dev']:
                    self._audio_dev = profile['audio_dev']['mic']
        if self._audio_dev is None:
            self._audio_dev = 0
        self.keep_files = False
        self.last_file_recorded = None

        self.start_background_threshold_thread()

    def start_background_threshold_thread(self):
        cls = self.__class__
        if cls._background_threshold_thread is None:
            self._logger.info("Starting background threshold monitoring")
            cls._background_threshold_thread = threading.Thread(target=self.backgroundThreshold)
            cls._background_threshold_thread.setDaemon(True)
            cls._background_threshold_thread.setName('noise_threadhold_monitor')
            cls._background_threshold_thread.start()

    def __del__(self):
        self._audio.terminate()

    @classmethod
    def setSpeaker(cls, speaker):
        cls.speaker = speaker

    def getScore(self, data):
        rms = audioop.rms(data, 2)
        score = rms / 3
        return score

    def backgroundThreshold(self):
        cls = self.__class__
        while True:
            try:
                self._logger.debug('Starting background sound threshold run')
                cls._last_threshold = self.fetchThresholdInBackground()
                cls._last_threshold_time = time.time()
                self._logger.debug('Finsihed background sound threshold run')
            except IOError as e:
                self._logger.warning('backgroundThreshold got exception: {}'.format(repr(e)))

            time.sleep(300)

    def fetchThreshold(self):
        cls = self.__class__
        if cls._last_threshold is None or time.time() - cls._last_threshold_time > 900:
            try:
                self._logger.debug('Starting foreground sound threshold run')
                cls._last_threshold = self.fetchThresholdInBackground()
                cls._last_threshold_time = time.time()
                self._logger.debug('Finsihed foreground sound threshold run')
            except IOError as e:
                self._logger.warning('FetchThreshold got exception: {}'.format(repr(e)))
        self._logger.debug('returned threshold is {}'.format(cls._last_threshold))
        return cls._last_threshold

    def fetchThresholdInBackground(self):
        cls = self.__class__

        # TODO: Consolidate variables from the next three functions
        THRESHOLD_MULTIPLIER = 1.8
        # RATE = 16000
        RATE = 44100
        # RATE = 8000
        # CHUNK = 1024
        CHUNK = 32

        # number of seconds to allow to establish threshold
        THRESHOLD_TIME = 1

        stream = None
        cls.lock.acquire()
        try:

            # prepare recording stream
            stream = self._audio.open(format=pyaudio.paInt16,
                                    channels=1,
                                    rate=RATE,
                                    input=True,
                                    input_device_index=self._audio_dev,
                                    frames_per_buffer=CHUNK)

            # stores the audio data
            frames = []

            # stores the lastN score values
            lastN = [i for i in range(int(20480/CHUNK))]

            # calculate the long run average, and thereby the proper threshold
            for i in range(0, int(RATE / CHUNK * THRESHOLD_TIME + 0.5)):

                # This is a poorly documentd hack to avoid buffer overflows on some platforms
                # Only works with pyaudio 0.2.11 and up
                data = stream.read(CHUNK, False)
                # data = stream.read(CHUNK)
                frames.append(data)

                # save this data point as a score
                lastN.pop(0)
                lastN.append(self.getScore(data))
                average = sum(lastN) / len(lastN)

        finally :
            if stream is not None:
                stream.stop_stream()
                stream.close()
            cls.lock.release()

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
                                  input_device_index=self._audio_dev,
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

        cls = self.__class__
        TARGET_RATE = 16000
        # RATE = 16000
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
                raise phone.Hangup()

        if not self.phone.ptt_pressed():
            return ['',]

        cls.lock.acquire()

        stream = None
        self.speaker.play(jasperpath.data('audio', 'beep_hi.wav'))

        try:
            # prepare recording stream
            stream = self._audio.open(format=pyaudio.paInt16,
                                    channels=1,
                                    rate=RATE,
                                    input=True,
                                    input_device_index=self._audio_dev,
                                    frames_per_buffer=CHUNK)

            frames = []
            # increasing the range # results in longer pause after command
            # generation
            lastN = [THRESHOLD * 1.2 for i in range(int(30720/CHUNK))]

            for i in range(0, RATE / CHUNK * LISTEN_TIME):

                # Only works with pyaudio 0.2.11 and up
                data = stream.read(CHUNK, False)
                # data = stream.read(CHUNK)
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
        finally: 
            if stream is not None:
                stream.stop_stream()
                stream.close()

            cls.lock.release()

        with tempfile.NamedTemporaryFile(mode='w+b', suffix='.wav', delete=not self.keep_files) as f:
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
                if self.keep_files:
                    self.last_file_recorded = f.name
            else:
                resampled_file = resample(f.name, TARGET_RATE)
                f_prime = open(resampled_file)
                candidates = self.active_stt_engine.transcribe(f_prime)
                f_prime.close()
                if self._echo:
                    self.speaker.play(resampled_file)
                if self.keep_files:
                    self.last_file_recorded = resampled_file
                    os.remove(f.name)
                else:
                    os.remove(resampled_file)

            if candidates:
                self._logger.info('Got the following possible transcriptions:')
                for c in candidates:
                    self._logger.info(c)
            # f.close()
            return candidates

    def say(self, phrase,
            OPTIONS=" -vdefault+m3 -p 40 -s 160 --stdout > say.wav"):
        cls = self.__class__
        # alter phrase before speaking
        phrase = alteration.clean(phrase)
        cls.lock.acquire()
        try:
            self.speaker.say(phrase)
        finally:
            cls.lock.release()
        if self.phone.on_hook():
            raise phone.Hangup()

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
