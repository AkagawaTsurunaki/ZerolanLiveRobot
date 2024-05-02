import json
import os
import uuid
from os import PathLike
from typing import Any
from config import GLOBAL_CONFIG as G_CFG
import yaml

_tts_save_dir = G_CFG.text_to_speech.save_directory


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


def write_wav(wave_data):
    ran_file_name = uuid.uuid4()
    tmp_wav_file_path = os.path.join(_tts_save_dir, f'{ran_file_name}.wav')
    with open(file=tmp_wav_file_path, mode='wb') as wav_file:
        wav_file.write(wave_data)
    tmp_wav_file_path = tmp_wav_file_path.replace("/", "\\")
    return tmp_wav_file_path
