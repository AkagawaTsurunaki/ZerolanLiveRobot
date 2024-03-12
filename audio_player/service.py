import os
import sys
from dataclasses import dataclass
from os import PathLike
from threading import Event
from typing import List

from loguru import logger
from playsound import playsound

logger.remove()
handler_id = logger.add(sys.stderr, level="INFO")


@dataclass
class AudioPair:
    played: bool
    transcript: str
    wav_file_path: str | PathLike


# 用于记录
audio_list: List[AudioPair] = []

FLAG = True


def stop():
    global audio_list, FLAG
    audio_list = []
    FLAG = False


def is_over() -> bool:
    # 查询音频是否已经播完
    for audiopair in audio_list:
        if not audiopair.played:
            return False
    return True


def play(audio_pair: AudioPair):
    logger.debug('正在播放音频文件：{wav_file_path}')
    # 为了避免发生 259 错误，请务必使用绝对路径
    # 并且请自行搜索解决编码问题的方法，需要修改playsound源码
    wav_file_path = os.path.abspath(audio_pair.wav_file_path)
    playsound(wav_file_path)
    audio_pair.played = True
    logger.debug(f'音频文件播放完毕：{wav_file_path}')


def add_audio(wav_file_path: str | PathLike, transcript: str):
    audiopair = AudioPair(transcript=transcript, wav_file_path=wav_file_path, played=False)
    audio_list.append(audiopair)


def start(add_audio_event: Event):
    while FLAG:
        add_audio_event.wait()
        print('THIS IS RUNNING')
        if len(audio_list) > 0:
            for audio_pair in audio_list:
                if not audio_pair.played:
                    play(audio_pair)
            add_audio_event.clear()
