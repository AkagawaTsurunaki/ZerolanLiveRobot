import sys
import threading

from loguru import logger

import vad.service
from asr.pipeline import ASRPipeline, ASRModelQuery
from common.datacls import Transcript, ASRServiceStatus
from config import GLOBAL_CONFIG as G_CFG

# Config logger
logger.remove()
handler_id = logger.add(sys.stderr, level="INFO")

_selecting_wav_event: threading.Event
_transcript_list: list[Transcript]
_running: bool
_pipeline: ASRPipeline


def init():
    global _selecting_wav_event, _transcript_list, _running, _pipeline

    _transcript_list = []
    _running = False
    _selecting_wav_event = threading.Event()
    _pipeline = ASRPipeline(G_CFG)


def start():
    global _running

    _running = True
    _selecting_wav_event.set()
    while _running:
        if _selecting_wav_event.is_set():
            wav_file_path = vad.service.select_latest_unread()
            if wav_file_path:
                asr_response = _pipeline.predict(ASRModelQuery(wav_path=wav_file_path))
                if asr_response:
                    t = Transcript(is_read=False, content=asr_response.transcript)
                    _transcript_list.append(t)


def select_latest_unread() -> str | None:
    """
    Select the most recent unread item in the recognized speech sequence.
    :return:
    """
    if len(_transcript_list) > 0:
        unread_list = [transcript for transcript in _transcript_list if not transcript.is_read]
        if len(unread_list) > 0:
            latest_unread = unread_list[-1]
            for item in _transcript_list:
                item.is_read = True
            return latest_unread.content

    return None


def stop():
    global _running

    _running = False
    _selecting_wav_event.clear()
    logger.warning('ASR service has been stopped.')


def pause():
    if _selecting_wav_event.is_set():
        _selecting_wav_event.clear()
        logger.info('ASR service paused.')
    else:
        logger.warning('Invalid operation: ASR service has been paused.')


def resume():
    if not _selecting_wav_event.is_set():
        _selecting_wav_event.clear()
        logger.info('Audio player service resumed.')
    else:
        logger.warning('Invalid operation: Audio player service has been resumed.')


def status() -> ASRServiceStatus:
    if _running:
        if _selecting_wav_event.is_set():
            return ASRServiceStatus.RUNNING
        else:
            return ASRServiceStatus.PAUSED
    else:
        return ASRServiceStatus.STOP
