import os
import sys
from dataclasses import dataclass
from os import PathLike
from threading import Event
from typing import List

from loguru import logger
from playsound import playsound

import obs.service
import utils.util

logger.remove()
handler_id = logger.add(sys.stderr, level="INFO")


@dataclass
class AudioPair:
    played: bool
    transcript: str
    wav_file_path: str | PathLike


# 用于记录
g_audio_list: List[AudioPair] = []

g_is_service_running = False


def play(audio_pair: AudioPair):
    logger.debug('正在播放音频文件：{wav_file_path}')
    # 为了避免发生 259 错误，请务必使用绝对路径
    # 并且请自行搜索解决编码问题的方法，需要修改playsound源码
    wav_file_path = os.path.abspath(audio_pair.wav_file_path)
    # 写入文件
    obs.service.write_llm_output(audio_pair.transcript)
    playsound(wav_file_path)
    audio_pair.played = True
    logger.debug(f'音频文件播放完毕：{wav_file_path}')


def add_audio(wav_file_path: str | PathLike, transcript: str):
    audiopair = AudioPair(transcript=transcript, wav_file_path=wav_file_path, played=False)
    g_audio_list.append(audiopair)


def start(add_audio_event: Event):
    global g_is_service_running
    g_is_service_running = True
    while g_is_service_running:
        add_audio_event.wait()
        if len(g_audio_list) > 0:
            for audio_pair in g_audio_list:
                if not audio_pair.played:
                    play(audio_pair)
            add_audio_event.clear()
    add_audio_event.clear()


def stop():
    """
    终止本服务
    :return:
    """
    global g_audio_list, g_is_service_running
    # 停止死循环
    g_is_service_running = False
    # 保存所有的文件
    utils.util.save_service('audio_player', g_audio_list)
    return not g_is_service_running
