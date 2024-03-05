import os
from os import PathLike

from loguru import logger
from playsound import playsound

from audio_player import AudioPair

# 用于记录
audio_list = []

def save():
    # TODO: 以json格式保存转录本
    ...

def is_over() -> bool:
    # TODO: 查询音频是否已经播完
    ...


async def play(wav_file_path: str | PathLike, transcript: str, block=True):
    logger.debug('正在以' + ("阻塞" if block else "非阻塞") + f'模式播放音频文件：{wav_file_path}')
    # 为了避免发生 259 错误，请务必使用绝对路径
    # 并且请自行搜索解决编码问题的方法，需要修改playsound源码
    wav_file_path = os.path.abspath(wav_file_path)
    playsound(wav_file_path, block=block)
    logger.debug(f'音频文件播放完毕：{wav_file_path}')
    audio_list.append(AudioPair(transcript=transcript, wav_file_path=wav_file_path))
