import os.path
from pathlib import Path
from typing import LiteralString
from uuid import uuid4

import yaml
from loguru import logger

from services.playground.data import FileInfo


def find_dir(dir_path: str, tgt_dir_name: str) -> str | None:
    assert os.path.exists(dir_path), f"{dir_path} 不是合法路径"
    for dirpath, dirnames, filenames in os.walk(dir_path):
        for dirname in dirnames:
            if tgt_dir_name in dirname:
                path = os.path.join(dirpath, dirname)
                return path.replace("\\", "/")
    return None


def read_yaml(path: str):
    with open(path, mode="r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def try_create_dir(dir_path: str):
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    assert os.path.isdir(dir_path)


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


import os
import zipfile


def compress_directory(directory_path: str, output_zip_path: str):
    """
    将指定目录压缩为一个 ZIP 文件。

    参数：
    - directory_path: 要压缩的目录路径（str）
    - output_zip_path: 输出的 ZIP 文件路径（str）
    """
    # 检查目录是否存在
    if not os.path.isdir(directory_path):
        raise ValueError(f"指定的路径不是一个目录: {directory_path}")

    with zipfile.ZipFile(output_zip_path, 'a', zipfile.ZIP_DEFLATED) as zipf:
        # 遍历目录及其子目录
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                # 获取文件的完整路径
                file_path = os.path.join(root, file)
                # 获取文件在 ZIP 文件中的相对路径
                arcname = os.path.relpath(file_path, start=directory_path)
                # 将文件添加到 ZIP 文件中
                zipf.write(file_path, arcname=arcname)

    logger.info(f"目录已成功压缩为: {output_zip_path}")
