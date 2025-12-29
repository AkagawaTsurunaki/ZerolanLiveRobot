from live2d.utils.lipsync import WavHandler
import soundfile as sf
import time
from loguru import logger


class Live2DWaveHandler(WavHandler):
    def Start(self, filePath: str) -> None:
        # Use `soundfile` instead of `wave`, because it supports more audio types.
        self.ReleasePcmData()
        try:
            data, samplerate = sf.read(filePath, dtype='float32')

            self.sampleRate = samplerate
            self.numChannels = data.ndim if data.ndim > 1 else 1
            self.numFrames = len(data)

            self.pcmData = data

            if self.numChannels == 1:
                self.pcmData = self.pcmData.reshape(1, -1)
            else:
                self.pcmData = self.pcmData.T  # shape: (channels, frames)

            self.startTime = time.time()
            self.lastOffset = 0

        except Exception as e:
            logger.error(f"Failed to load audio: {e}")
            self.ReleasePcmData()
