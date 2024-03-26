from typing import List

import requests
from loguru import logger

import initzr
import vad.service
from utils.datacls import Transcript, HTTPResponseBody

# 该服务是否已被初始化?
g_is_service_inited = False

# 该服务是否正在运行?
g_is_service_running = False

# 识别出的每一条语音对应的 Transcript 放在这个列表中
g_transcript_list: List[Transcript] = []

URL = 'http://127.0.0.1:11005'


def select_latest_unread() -> str | None:
    """
    选择识别出的语音序列中最新未读的一项
    :return:
    """
    if len(g_transcript_list) > 0:
        unread_list = [transcript for transcript in g_transcript_list if not transcript.is_read]
        if len(unread_list) > 0:
            latest_unread = unread_list[-1]
            latest_unread.is_read = True
            return latest_unread.content

    return None


def _predict(wav_file_path: str):
    response = requests.get(url=f'{URL}/asr/predict', data={"wav_path": wav_file_path})
    response = HTTPResponseBody(**response.json())
    if response.ok:
        transcript = response.data.get('transcript', None)
        return transcript
    return None


def init():
    config = initzr.load_asr_config()


def start():
    global g_is_service_running
    g_is_service_running = True
    logger.info('👂️ 自动语音识别服务已启动')
    while g_is_service_running:
        wav_file_path = vad.service.select_latest_unread()
        if wav_file_path:
            res = _predict(wav_file_path)
            if res:
                g_transcript_list.append(
                    Transcript(is_read=False, content=res)
                )
