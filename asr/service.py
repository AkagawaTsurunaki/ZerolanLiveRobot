import sys
import threading
from dataclasses import dataclass
from typing import List

from loguru import logger

from vad.service import VADService
from asr.pipeline import ASRPipeline, ASRModelQuery
from common.abs_service import AbstractService, ServiceStatus
from config import GlobalConfig
from common.datacls import Transcript

# Config logger
logger.remove()
handler_id = logger.add(sys.stderr, level="INFO")


@dataclass
class ASRServiceStatus(ServiceStatus):
    RUNNING = 'RUNNING'
    PAUSED = 'PAUSED'
    STOP = 'STOP'


class ASRService(AbstractService):
    def __init__(self, cfg: GlobalConfig, vad_service: VADService):
        self.g_transcript_list: List[Transcript] = []
        self._running: bool = False
        self._selecting_wav_event: threading.Event = threading.Event()
        self._pipeline = ASRPipeline(cfg)
        self._vad_service = vad_service

    def start(self):
        self._running = True
        self._selecting_wav_event.set()
        logger.info('ASR service starting...')
        while self._running:
            if self._selecting_wav_event.is_set():
                wav_file_path = self._vad_service.select_latest_unread()
                if wav_file_path:
                    asr_response = self._pipeline.predict(ASRModelQuery(wav_path=wav_file_path))
                    if asr_response:
                        t = Transcript(is_read=False, content=asr_response.transcript)
                        self.g_transcript_list.append(t)

    def select_latest_unread(self) -> str | None:
        """
        Select the most recent unread item in the recognized speech sequence.
        :return:
        """
        if len(self.g_transcript_list) > 0:
            unread_list = [transcript for transcript in self.g_transcript_list if not transcript.is_read]
            if len(unread_list) > 0:
                latest_unread = unread_list[-1]
                for item in self.g_transcript_list:
                    item.is_read = True
                return latest_unread.content

        return None

    def stop(self):
        self._running = False
        self._selecting_wav_event.clear()
        logger.warning('ASR service has been stopped.')

    def pause(self):
        if self._selecting_wav_event.is_set():
            self._selecting_wav_event.clear()
            logger.info('ASR service paused.')
        else:
            logger.warning('Invalid operation: ASR service has been paused.')

    def resume(self):
        if not self._selecting_wav_event.is_set():
            self._selecting_wav_event.clear()
            logger.info('Audio player service resumed.')
        else:
            logger.warning('Invalid operation: Audio player service has been resumed.')

    def status(self) -> ASRServiceStatus:
        if self._running:
            if self._selecting_wav_event.is_set():
                return ASRServiceStatus.RUNNING
            else:
                return ASRServiceStatus.PAUSED
        else:
            return ASRServiceStatus.STOP
