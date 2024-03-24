from dataclasses import dataclass
from os import PathLike
from typing import List

from funasr import AutoModel
from loguru import logger

import vad.service

MODEL: AutoModel


@dataclass
class UserQuery:
    is_read: bool
    content: str


user_query_list: List[UserQuery] = []


def init(model_path: str | PathLike, vad_model_path: str | PathLike) -> bool:
    global MODEL
    MODEL = AutoModel(model=model_path, model_revision="v2.0.4",
                      vad_model=vad_model_path, vad_model_revision="v2.0.4",
                      # punc_model="ct-punc-c", punc_model_revision="v2.0.4",
                      # spk_model="cam++", spk_model_revision="v2.0.2",
                      )
    return True


def predict(wav_path) -> str | None:
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
    logger.info('语音识别服务已启动')
    while True:
        wav_file_path = vad.service.select01()
        if wav_file_path:
            res = predict(wav_file_path)
            if res:
                user_query_list.append(
                    UserQuery(is_read=False, content=res)
                )
                logger.info(res)
