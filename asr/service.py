from typing import List

from loguru import logger

import vad.service
from asr.api import predict
from utils.datacls import Transcript

# 识别出的每一条语音对应的 Transcript 放在这个列表中
g_transcript_list: List[Transcript] = []


def select_latest_unread() -> str | None:
    """
    选择识别出的语音序列中最新未读的一项
    :return:
    """
    if len(g_transcript_list) > 0:
        unread_list = [transcript for transcript in g_transcript_list if not transcript.is_read]
        if len(unread_list) > 0:
            latest_unread = unread_list[-1]
            for item in g_transcript_list:
                item.is_read = True
            return latest_unread.content

    return None


def start():
    logger.info('👂️ 自动语音识别服务已启动')
    while True:
        wav_file_path = vad.service.select_latest_unread()
        if wav_file_path:
            res = predict(wav_file_path)
            if res:
                g_transcript_list.append(
                    Transcript(is_read=False, content=res)
                )
