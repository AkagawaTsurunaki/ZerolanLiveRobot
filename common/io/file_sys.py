import os
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Literal

from typeguard import typechecked


def get_time_string():
    current_time = datetime.now()
    time_str = current_time.strftime("%Y%m%d%H%M%S")
    return time_str


ResType = Literal["image", "video", "audio", "model"]


class FileSystem:
    def __init__(self):
        self._proj_dir: Path | None = None
        self._temp_dir: Path | None = None
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
    def create_temp_file_descriptor(self, prefix: str, suffix: str, type: ResType) -> Path:
        """
        Create temp file descriptor.
        :param prefix: Prefix that at the beginning of the file name.
        :param suffix: Suffix that at the end of the file name. Usually file type. For example .wav
        :param type: Temp resource type. See ResType.
        :return:
        """
        self.temp_dir.mkdir(exist_ok=True)
        if suffix[0] == '.':
            suffix = suffix[1:]
        filename = f"{prefix}-{get_time_string()}.{suffix}"
        typed_dir = self.temp_dir.joinpath(type)
        typed_dir.mkdir(exist_ok=True)
        return typed_dir.joinpath(filename).absolute()

    @typechecked
    def find_dir(self, dir_path: str, tgt_dir_name: str) -> Path | None:
        """
        Walk in tgt_dir_name, and find if dir_path exists
        :param dir_path: Directory path to walk.
        :param tgt_dir_name: Target directory name to find.
        :return: Path if found, else None
        """
        assert os.path.exists(dir_path), f"{dir_path} doesn't exist."
        for dirpath, dirnames, filenames in os.walk(dir_path):
            for dirname in dirnames:
                if tgt_dir_name in dirname:
                    path = os.path.join(dirpath, dirname)
                    return Path(path).absolute()
        return None

    @typechecked
    def compress(self, src_dir: str | Path, tgt_dir: str | Path):
        src_dir = Path(src_dir).absolute()

        with zipfile.ZipFile(tgt_dir, 'a', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(src_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, start=src_dir)
                    zipf.write(file_path, arcname=arcname)


fs = FileSystem()
