import io
import threading
import wave

import pyaudio
import webrtcvad
from loguru import logger

from common.concurrent.abs_runnable import ThreadRunnable
from common.io.file_type import AudioFileType
from event.event_data import SpeechEvent
from event.event_emitter import emitter


class SmartMicrophone(ThreadRunnable):
    def __init__(self, vad_mode=0, frame_duration=30):
        """
        初始化智能麦克风类
        :param vad_mode: Optionally, set its aggressiveness mode, which is an integer between 0 and 3.
                         0 is the least aggressive about filtering out non-speech, 3 is the most aggressive.
        :param frame_duration: A frame must be either 10, 20, or 30 ms in duration.
        """
        super().__init__()
        assert frame_duration in [10, 20, 30], f"A frame must be either 10, 20, or 30 ms in duration!"

        # Audio parameters
        self._format = pyaudio.paInt16
        self._channels = 1
        self._sample_rate = 16000
        self._chunk_size = int(self._sample_rate * frame_duration / 1000)  # Bytes

        # Initialize microphone
        self._audio = pyaudio.PyAudio()
        self._vad = webrtcvad.Vad(vad_mode)
        self._stream = self._audio.open(format=self._format,
                                        channels=self._channels,
                                        rate=self._sample_rate,
                                        input=True,
                                        frames_per_buffer=self._chunk_size)

        self._audio_frames = []
        self._is_speaking = False

        self._pause_event = threading.Event()
        self._stop_flag = False

    def start(self):
        super().start()
        self._pause_event.set()
        self._stop_flag = False
        try:
            while not self._stop_flag:
                self._pause_event.wait()
                if self._stop_flag:
                    break
                data = self._stream.read(self._chunk_size, exception_on_overflow=False)
                if self._vad.is_speech(data, self._sample_rate):
                    if not self._is_speaking:
                        logger.info("Voice detected: Beginning.")
                        self._is_speaking = True
                    self._audio_frames.append(data)
                else:
                    if self._is_speaking:
                        logger.info("Voice detected: Ending.")
                        self._is_speaking = False
                        self._emit_event()
                        self._audio_frames = []
        except Exception as e:
            logger.exception(e)
        finally:
            # Stop and close the microphone stream
            self._stream.stop_stream()
            self._stream.close()
            self._audio.terminate()

    def _emit_event(self):
        if self._audio_frames:
            # 创建一个BytesIO对象来存储WAV文件
            file = io.BytesIO()
            wf = wave.open(file, 'wb')
            wf.setnchannels(self._channels)
            wf.setsampwidth(self._audio.get_sample_size(self._format))
            wf.setframerate(self._sample_rate)
            wf.writeframes(b''.join(self._audio_frames))
            wf.close()

            # 将BytesIO对象的指针移到开始位置
            file.seek(0)
            emitter.emit(SpeechEvent(
                speech=file.read(),
                audio_type=AudioFileType.WAV,
                channels=self._channels,
                sample_rate=self._sample_rate,
            ))

    def pause(self):
        self._pause_event.clear()
        logger.info("Paused smart microphone.")

    def resume(self):
        self._pause_event.set()
        logger.info("Resumed smart microphone.")

    def stop(self):
        self._stop_flag = True
        self._pause_event.set()
        logger.info("Stopped smart microphone.")

    def name(self):
        return "SmartMicrophone"