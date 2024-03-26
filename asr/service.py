import threading
from dataclasses import asdict
from os import PathLike
from typing import List

from funasr import AutoModel
from loguru import logger

import vad.service
from utils.datacls import Transcript
from utils.util import save_service

# 该服务是否已被初始化?
g_is_service_inited = False

# 该服务是否正在运行?
g_is_service_running = False

# 该服务是否暂停
g_pause_event = threading.Event()

# 识别出的每一条语音对应的 Transcript 放在这个列表中
g_transcript_list: List[Transcript] = []

# 推理模型
MODEL: AutoModel


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


def init(model_path: str | PathLike, vad_model_path: str | PathLike) -> bool:
    global MODEL, g_is_service_inited
    if vad_model_path:
        logger.warning('⚠️ 使用 VAD 模型可能会出现疑难杂症，建议不要使用')
    MODEL = AutoModel(model=model_path, model_revision="v2.0.4",
                      # vad_model=vad_model_path, vad_model_revision="v2.0.4",
                      # punc_model="ct-punc-c", punc_model_revision="v2.0.4",
                      # spk_model="cam++", spk_model_revision="v2.0.2",
                      )
    g_is_service_inited = True
    logger.info('👂️ 自动语音识别服务初始化完毕')
    return g_is_service_inited


def predict(wav_path) -> str | None:
    assert g_is_service_inited, f'❌ 自动语音识别服务未初始化'
    try:
        res = MODEL.generate(input=wav_path,
                             batch_size_s=300,
                             hotword='魔搭')
        res = res[0]['text']
        return res
    except Exception as e:
        logger.exception(e)
        return None


def start():
    global g_is_service_running
    g_is_service_running = True
    g_pause_event.set()
    logger.info('👂️ 自动语音识别服务已启动')
    while g_is_service_running:
        g_pause_event.wait()
        wav_file_path = vad.service.select_latest_unread()
        if wav_file_path:
            res = predict(wav_file_path)
            if res:
                g_transcript_list.append(
                    Transcript(is_read=False, content=res)
                )


def pause():
    g_pause_event.clear()
    logger.info('⏸️ 自动语音识别服务暂停')


def resume():
    g_pause_event.set()
    logger.info('▶️ 自动语音识别服务继续')


def stop():
    global g_is_service_running, g_transcript_list, g_is_service_inited
    g_is_service_running = False
    g_is_service_inited = False
    obj = [asdict(item) for item in g_transcript_list]
    save_service('asr', obj)
    g_transcript_list = []
    logger.warning('⏹️ 自动语音识别服务终止')
