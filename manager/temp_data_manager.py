import os

from common.utils.file_util import try_create_dir


class TempDataManager:
    def __init__(self):
        self.current_work_dir = os.getcwd()
        self._temp_dir = os.path.join(self.current_work_dir, ".temp")
        self.create_temp_dir()

    def create_temp_dir(self):
        temp_dir = self._temp_dir
        try_create_dir(temp_dir)

        for dir_name in ["image", "audio", "video", "model"]:
            dir_path = os.path.join(temp_dir, dir_name)
            try_create_dir(dir_path)

    @staticmethod
    def remove_temp_dir():
        raise Exception("Remove them manually! For safety!")
