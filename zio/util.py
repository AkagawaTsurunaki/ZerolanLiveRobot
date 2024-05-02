import json
import os
from os import PathLike
from typing import Any

import yaml


def save_json(file_path: str | os.PathLike, obj: Any):
    """
    Save JSON file.
    :param file_path: Path of file.
    :param obj: Any object that can be serialized as JSON.
    :return:
    """
    dir_path = os.path.dirname(file_path)
    os.makedirs(dir_path, exist_ok=True)
    with open(file=file_path, mode='w+', encoding='utf-8') as file:
        json.dump(fp=file, obj=obj)


def read_json(path: str | os.PathLike) -> Any:
    assert os.path.exists(path)
    with open(file=path, encoding='utf-8', mode='r') as file:
        return json.load(file)


def read_yaml(path: str | PathLike):
    with open(file=path, mode='r', encoding='utf-8') as file:
        return yaml.safe_load(file)

