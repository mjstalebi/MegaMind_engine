import time, logging
from datetime import datetime
import threading, collections, queue
import deepspeech
import numpy as np
import pyaudio
import wave
import webrtcvad
from halo import Halo
from scipy import signal

import os
import threading
import time

DEFAULT_SAMPLE_RATE = 16000

play_done = False


def log_time(mystr):
	test_file = open('/tmp/MegsTST.txt','a+')
	milliseconds = int(round(time.time() * 1000)) 
#	test_file.write(str(milliseconds) + '\t' + mystr +'\n')
	test_file.write( mystr + '\t'+str(milliseconds)  + '\n')
	test_file.flush()
	test_file.close()
	return

class Audio(object):
    """Streams raw audio from microphone. Data is received in a separate thread, and stored in a buffer, to be read from."""

    FORMAT = pyaudio.paInt16
    # Network/VAD rate-space
    RATE_PROCESS = 16000
    CHANNELS = 1
    BLOCKS_PER_SECOND = 50

    def __init__(self, callback=None, device=None, input_rate=RATE_PROCESS, file=None):
        def proxy_callback(in_data, frame_count, time_info, status):
            #pylint: disable=unused-argument
            if self.chunk is not None:
                in_data = self.wf.readframes(self.chunk)
            callback(in_data)
            return (None, pyaudio.paContinue)
        if callback is None: callback = lambda in_data: self.buffer_queue.put(in_data)
        self.buffer_queue = queue.Queue()
        self.device = device
        self.input_rate = input_rate
        self.sample_rate = self.RATE_PROCESS
        self.block_size = int(self.RATE_PROCESS / float(self.BLOCKS_PER_SECOND))
        self.block_size_input = int(self.input_rate / float(self.BLOCKS_PER_SECOND))
        self.pa = pyaudio.PyAudio()

        kwargs = {
            'format': self.FORMAT,
            'channels': self.CHANNELS,
            'rate': self.input_rate,
            'input': True,
            'frames_per_buffer': self.block_size_input,
            'stream_callback': proxy_callback,
        }

        self.chunk = None
        # if not default device
        if self.device:
            kwargs['input_device_index'] = self.device
        elif file is not None:
            self.chunk = 320
            self.wf = wave.open(file, 'rb')

        self.stream = self.pa.open(**kwargs)
        self.stream.start_stream()

    def resample(self, data, input_rate):
        """
        Microphone may not support our native processing sampling rate, so
        resample from input_rate to RATE_PROCESS here for webrtcvad and
        deepspeech

        Args:
            data (binary): Input audio stream
            input_rate (int): Input audio rate to resample from
        """
        data16 = np.fromstring(string=data, dtype=np.int16)
        resample_size = int(len(data16) / self.input_rate * self.RATE_PROCESS)
        resample = signal.resample(data16, resample_size)
        resample16 = np.array(resample, dtype=np.int16)
        return resample16.tostring()

    def read_resampled(self):
        """Return a block of audio data resampled to 16000hz, blocking if necessary."""
        return self.resample(data=self.buffer_queue.get(),
                             input_rate=self.input_rate)

    def read(self):
        """Return a block of audio data, blocking if necessary."""
        return self.buffer_queue.get()

    def destroy(self):
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()

    frame_duration_ms = property(lambda self: 1000 * self.block_size // self.sample_rate)

    def write_wav(self, filename, data):
        logging.info("write wav %s", filename)
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.CHANNELS)
        # wf.setsampwidth(self.pa.get_sample_size(FORMAT))
        assert self.FORMAT == pyaudio.paInt16
        wf.setsampwidth(2)
        wf.setframerate(self.sample_rate)
        wf.writeframes(data)
        wf.close()


class VADAudio(Audio):
    """Filter & segment audio with voice activity detection."""

    def __init__(self, aggressiveness=3, device=None, input_rate=None, file=None):
        super().__init__(device=device, input_rate=input_rate, file=file)
        self.vad = webrtcvad.Vad(aggressiveness)

    def frame_generator(self):
        """Generator that yields all audio frames from microphone."""
        if self.input_rate == self.RATE_PROCESS:
            while True:
                yield self.read()
        else:
            while True:
                yield self.read_resampled()

    def vad_collector(self, padding_ms=300, ratio=0.75, frames=None):
        """Generator that yields series of consecutive audio frames comprising each utterence, separated by yielding a single None.
            Determines voice activity by ratio of frames in padding_ms. Uses a buffer to include padding_ms prior to being triggered.
            Example: (frame, ..., frame, None, frame, ..., frame, None, ...)
                      |---utterence---|        |---utterence---|
        """
        if frames is None: frames = self.frame_generator()
        num_padding_frames = padding_ms // self.frame_duration_ms
        ring_buffer = collections.deque(maxlen=num_padding_frames)
        triggered = False

        for frame in frames:
            if len(frame) < 640:
                return

            is_speech = self.vad.is_speech(frame, self.sample_rate)

            if not triggered:
                ring_buffer.append((frame, is_speech))
                num_voiced = len([f for f, speech in ring_buffer if speech])
                if num_voiced > ratio * ring_buffer.maxlen:
                    triggered = True
                    for f, s in ring_buffer:
                        yield f
                    ring_buffer.clear()

            else:
                yield frame
                ring_buffer.append((frame, is_speech))
                num_unvoiced = len([f for f, speech in ring_buffer if not speech])
                if num_unvoiced > ratio * ring_buffer.maxlen:
                    triggered = False
                    yield None
                    ring_buffer.clear()

def play_thread(name,file_name):
	os.system('play ' + file_name)
	log_time('Audio play done')	
	return
#class DeepSpeech:
#	def __init__(self):
#		dirName = os.path.expanduser('deep_speech_models')
#		self.dir_audio = 'audio_tests/'
#		# Resolve all the paths of model files
#		output_graph, scorer = wavTranscriber.resolve_models(dirName)		
#		# Load output_graph, alpahbet and scorer
#		self.model_retval = wavTranscriber.load_model(output_graph, scorer)
#	def convert(self, test_id , test_num):
#		audio_file = self.dir_audio + test_id + '/' + test_num + '.wav'
#		th1 = threading.Thread(target=play_thread, args=(1,audio_file), daemon=False)
#		th1.start()
#		waveFile = audio_file
#		segments, sample_rate, audio_length = wavTranscriber.vad_segment_generator(waveFile, 0)
#		text = ''
#		inference_time = 0.0
#		for i, segment in enumerate(segments):
#			# Run deepspeech on the chunk that just completed VAD
#			audio = np.frombuffer(segment, dtype=np.int16)
#			output = wavTranscriber.stt(self.model_retval[0], audio, sample_rate)
#			inference_time += output[1]
#			text += output[0]
#		print(text, 'audio len= ', audio_length, ' infrence_time= ', inference_time)	
#		th1.join()
#		return
#

class DeepSpeech:
	def __init__(self):
		dirName = os.path.expanduser('deep_speech_models')
		model_path = dirName + '/deepspeech-0.7.0-models.pbmm'
		scorer_path = dirName + '/deepspeech-0.7.0-models.scorer'
		self.dir_audio = 'audio_tests/'
		self.model = deepspeech.Model(model_path)
		self.model.enableExternalScorer(scorer_path)
	def convert(self, test_id , test_num):
		audio_file = self.dir_audio + test_id + '/' + test_num + '.wav'
		print('Deep speech convert start')
		th1 = threading.Thread(target=play_thread, args=(1,audio_file), daemon=False)
		th1.start()
		audio_file = self.dir_audio + test_id + '/' + test_num + '_long.wav'
		vad_audio = VADAudio(aggressiveness=3,
                         device=None,
                         input_rate=DEFAULT_SAMPLE_RATE,
                         file=audio_file)
		frames = vad_audio.vad_collector()
		stream_context = self.model.createStream()
		for frame in frames:
			if frame is not None:
				logging.debug("streaming frame")
				stream_context.feedAudioContent(np.frombuffer(frame, np.int16))
			else:
				logging.debug("end utterence")
				text = stream_context.finishStream()
				print("Recognized: %s" % text)
				th1.join()
				log_time('Recognize done')
				return text


