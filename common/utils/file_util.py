import os.path
from pathlib import Path
from typing import LiteralString
from uuid import uuid4

import yaml

from services.playground.data import FileInfo


def read_yaml(path: str):
    with open(path, mode="r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_file_info(path: LiteralString | str | bytes) -> FileInfo:
    assert os.path.exists(path)
    path = str(path)
    file_extension = Path(path).suffix
    file_name = Path(path).name
    # file_name = file_name[:len(file_name) - len(file_extension)]
    if file_extension is not None and len(file_extension) > 1:
        file_extension = file_extension[1:]
    file_size = os.path.getsize(path)
    return FileInfo(
        file_id=f"{uuid4()}",
        uri=path_to_uri(path),
        file_type=file_extension,
        origin_file_name=file_name,
        file_name=file_name,
        file_size=file_size,
    )


def path_to_uri(path):
    path = os.path.abspath(path)
    path = path.replace('\\', '/')
    uri = f'file:///{path}'
    return uri
