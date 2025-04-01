import hashlib
import os
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Literal, TypeVar

from typeguard import typechecked


def calculate_path_md5(file_path):
    """
    计算文件路径的 MD5 值
    :param file_path: 文件路径
    :return: MD5 值的十六进制字符串
    """
    md5 = hashlib.md5()
    # 将路径编码为字节（通常是 UTF-8）
    path_bytes = file_path.encode('utf-8')
    # 更新哈希对象
    md5.update(path_bytes)
    # 返回十六进制的 MD5 值
    return md5.hexdigest()


class FileType(str, Enum):
    WAV = 'wav'
    OGG = 'ogg'
    MP3 = 'mp3'


def get_time_string():
    current_time = datetime.now()
    time_str = current_time.strftime("%Y%m%d%H%M%S")
    return time_str


ResType = Literal["image", "video", "audio", "model"]


class FileSystem:
    def __init__(self):
        self._proj_dir: Path | None = None
        self._temp_dir: Path | None = None

        self.temp_files = {}

        self._create_temp_dir()

    def _create_temp_dir(self):
        self.temp_dir.mkdir(exist_ok=True)
        for dir_name in ["image", "audio", "video", "model"]:
            self.temp_dir.joinpath(dir_name).mkdir(exist_ok=True)

    @property
    def project_dir(self) -> Path:
        """
        Get project directory path.
        :return: Project directory path.
        """
        if self._proj_dir is None:
            cur_work_dir = os.getcwd()
            if Path(cur_work_dir).name == "tests":
                dir_path = Path(cur_work_dir).parent
                self._proj_dir = Path(dir_path)
            else:
                self._proj_dir = Path(cur_work_dir)
        return self._proj_dir.absolute()

    @property
    def temp_dir(self) -> Path:
        """
        Get temp directory path.
        :return: Temp directory path.
        """
        if self._temp_dir is None:
            self._temp_dir = self.project_dir.joinpath('.temp/')
        return self._temp_dir.absolute()

    @typechecked
    def create_temp_file_descriptor(self, prefix: str, suffix: str, type: ResType):
        self.temp_dir.mkdir(exist_ok=True)
        if suffix[0] == '.':
            suffix = suffix[1:]
        filename = f"{prefix}-{get_time_string()}{suffix}"
        typed_dir = self.temp_dir.joinpath(type)
        typed_dir.mkdir(exist_ok=True)
        return typed_dir.joinpath(filename).absolute()


fs = FileSystem()
