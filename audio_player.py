import os
from dataclasses import dataclass
from os import PathLike
from queue import Queue
import threading
from loguru import logger
from playsound import playsound


@dataclass
class AudioPair:
    text: str
    wav_file_path: str | PathLike


class AudioPlayer:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.__initialized = False
            return cls._instance

    def __init__(self):
        if self.__initialized:
            return
        self.__initialized = True
        self.__audio_list = Queue()

    def add(self, text, wav_file_path):
        """
        向音频队列中增加一个音频
        :param text: 音频文本
        :param wav_file_path: 音频文件路径
        :return:
        """
        self.__audio_list.put(AudioPair(text, wav_file_path))
        logger.info(f'put {wav_file_path}')

    def play(self):
        audio_pair = self.__audio_list.get()
        if audio_pair is not None:
            self.__play(audio_pair.wav_file_path)

    def __play(self, wav_file_path: str | PathLike, block=True):
        logger.info('正在以' + ("阻塞" if block else "非阻塞") + f'模式播放音频文件：{wav_file_path}')
        # 为了避免发生 259 错误，请务必使用绝对路径
        # 并且请自行搜索解决编码问题的方法，需要修改playsound源码
        wav_file_path = os.path.abspath(wav_file_path)
        playsound(wav_file_path, block=block)
        logger.info(f'音频文件播放完毕：{wav_file_path}')

    def is_empty(self):
        return self.__audio_list.empty()

    def start(self):
        while True:
            try:
                self.play()
            except Exception:
                pass
