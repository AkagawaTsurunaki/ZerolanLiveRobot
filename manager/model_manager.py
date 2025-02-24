import os
from typing import Dict, List, LiteralString

from loguru import logger

from common.data import FileInfo
from common.utils.file_util import get_file_info


class ModelManager:
    def __init__(self, model_dir=None):
        self._model_dir = R".\resources\static\models\3d" if model_dir is None else model_dir
        self._model_files: Dict[str, FileInfo] = {}

    def scan(self):
        for root, dirs, files in os.walk(self._model_dir):
            for file in files:
                filepath = os.path.join(root, file)
                file_info = get_file_info(filepath)
                self._model_files[file_info.file_id] = file_info
                logger.info(f"{file_info.file_name} is registered as {file_info.file_id}")

    def get_files(self) -> List[dict]:
        files = []
        for _, file_info in self._model_files.items():
            files.append({
                "id": file_info.file_id,
                "filename": file_info.file_name,
            })
        return files

    def get_file_by_id(self, file_id: str) -> FileInfo:
        return self._model_files[file_id]
