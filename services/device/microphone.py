from typing import Generator, Any

import pyaudio
from loguru import logger


class Microphone:

    def __init__(self):
        """
        Note:
            The bytes type is returned after the audio is sampled, but when converted with numpy,
            the dtype type of the numpy vector must match the format of the data format using the microphone,
            otherwise an exception may occur.
        """
        self._stream: pyaudio.Stream = None
        self._chunk_size = 4096  # The size of the audio data read at a time
        self._format = pyaudio.paFloat32  # TODO: The format in which the audio is recorded, temporarily hardcoded to Float32 format to prevent possible errors
        self.channels = 1
        self.sample_rate = 16000
        self._p = pyaudio.PyAudio()
        self._chunk_stride: int = 960 * 10
        self._is_recording: bool = False

    def open(self):
        logger.info("Open the microphone")
        if self._is_recording:
            logger.warning("Microphone recording...")
            return
        self._is_recording = True
        self._stream = self._p.open(format=self._format,
                                    channels=self.channels,
                                    rate=self.sample_rate,
                                    input=True,
                                    frames_per_buffer=self._chunk_size)

    def close(self):
        self._stream.stop_stream()
        self._stream.close()

        self._p.terminate()
        self._is_recording = False
        logger.info("Close the microphone")

    def stream(self) -> Generator[bytes | None, Any, None]:
        try:
            while True:
                data = self._stream.read(self._chunk_stride)
                yield data
        except Exception as e:
            logger.exception(e)
            yield None

    @property
    def is_recording(self):
        return self._is_recording
