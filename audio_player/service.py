import os
import sys
import threading
from os import PathLike
from typing import List

from loguru import logger
from playsound import playsound

import obs.service
import utils.util
from utils.datacls import AudioPair

logger.remove()
handler_id = logger.add(sys.stderr, level="INFO")

# 用于记录
g_audio_list: List[AudioPair] = []

g_is_service_running = False

# 音频加入线程事件, 只有新的音频加入后, 播放线程才会播放音频, 减少 CPU 占用
g_add_audio_event = threading.Event()

# 音频播放事件, 用于控制是否进行播放
g_audio_play_event = threading.Event()


def play(audio_pair: AudioPair):
    # 为了避免发生 259 错误，请务必使用绝对路径
    # 并且请自行搜索解决编码问题的方法，需要修改playsound源码
    wav_file_path = os.path.abspath(audio_pair.wav_file_path)
    logger.debug(f'正在播放音频文件：{wav_file_path}')
    # 写入文件
    obs.service.write_llm_output(audio_pair.transcript)
    playsound(wav_file_path)
    audio_pair.played = True
    logger.debug(f'音频文件播放完毕：{wav_file_path}')


def add_audio(wav_file_path: str | PathLike, transcript: str):
    audiopair = AudioPair(transcript=transcript, wav_file_path=wav_file_path, played=False)
    g_audio_list.append(audiopair)
    g_add_audio_event.set()


def start():
    global g_is_service_running
    g_is_service_running = True
    g_audio_play_event.set()
    while g_is_service_running:
        g_add_audio_event.wait()
        g_audio_play_event.wait()
        if len(g_audio_list) > 0:
            for audio_pair in g_audio_list:
                if not audio_pair.played:
                    play(audio_pair)
            g_add_audio_event.clear()
    g_add_audio_event.clear()


def switch():
    if g_add_audio_event.is_set():
        g_add_audio_event.clear()
        logger.info('⏸️ 音频播放服务暂停')
        return False
    else:
        g_add_audio_event.set()
        logger.info('▶️ 音频播放服务继续')
        return True


def stop():
    global g_audio_list, g_is_service_running
    # 停止死循环
    g_is_service_running = False
    # 保存所有的文件
    utils.util.save_service('audio_player', g_audio_list)
    g_audio_list = []
    logger.warning('音频播放服务已终止')
    return not g_is_service_running
