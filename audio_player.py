from dataclasses import dataclass
from os import PathLike
from queue import Queue

from loguru import logger
from playsound import playsound

__audio_list = Queue()


@dataclass
class AudioPair:
    text: str
    wav_file_path: str | PathLike


def add(text, wav_file_path):
    """
    向音频队列中增加一个音频
    :param text:
    :param wav_file_path:
    :return:
    """
    __audio_list.put(AudioPair(text, wav_file_path))
    logger.info(f'put{wav_file_path}')


def play():
    audio_pair = __audio_list.get()
    if audio_pair is not None:
        __play(audio_pair.wav_file_path)


def __play(wav_file_path: str | PathLike, block=True):
    logger.info('正在以' + "阻塞" if block else "非阻塞" + f'模式播放音频文件：{wav_file_path}')
    playsound(wav_file_path, block=block)
    logger.info(f'音频文件播放完毕：{wav_file_path}')


def start():
    while True:
        play()
