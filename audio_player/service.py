import os
from dataclasses import dataclass
from os import PathLike

from loguru import logger
from playsound import playsound

@dataclass
class AudioPair:
    text: str
    wav_file_path: str | PathLike


def is_over() -> bool:
    ...


async def play(wav_file_path: str | PathLike, block=True):
    logger.debug('正在以' + ("阻塞" if block else "非阻塞") + f'模式播放音频文件：{wav_file_path}')
    # 为了避免发生 259 错误，请务必使用绝对路径
    # 并且请自行搜索解决编码问题的方法，需要修改playsound源码
    wav_file_path = os.path.abspath(wav_file_path)
    playsound(wav_file_path, block=block)
    logger.debug(f'音频文件播放完毕：{wav_file_path}')
