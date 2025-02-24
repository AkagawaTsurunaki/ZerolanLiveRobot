import os
import os.path
import uuid
from pathlib import Path
from time import time
from typing import Literal, LiteralString
from uuid import uuid4

import yaml

from common.data import FileInfo


def get_real_project_dir() -> Path:
    """
    获取项目的真实路径。
    为了避免在 tests 文件夹下找不到相对路径。
    :return:
    """
    cur_work_dir = os.getcwd()
    if Path(cur_work_dir).name == "tests":
        return Path(cur_work_dir).parent
    else:
        return Path(cur_work_dir)


project_dir = get_real_project_dir()
temp_data_dir = os.path.join(project_dir, ".temp/")


def find_dir(dir_path: str, tgt_dir_name: str) -> str | None:
    assert os.path.exists(dir_path), f"{dir_path} 不是合法路径"
    for dirpath, dirnames, filenames in os.walk(dir_path):
        for dirname in dirnames:
            if tgt_dir_name in dirname:
                path = os.path.join(dirpath, dirname)
                return path.replace("\\", "/")
    return None


def create_temp_file(prefix: str, suffix: str, tmpdir: Literal["image", "video", "audio"]) -> str:
    tmp_dir = os.path.join(temp_data_dir, tmpdir)
    tmp_dir = os.path.abspath(tmp_dir)
    temp_file_path = os.path.join(f"{tmp_dir}", f"{prefix}-{time()}-{uuid.uuid4()}{suffix}")
    temp_file_path = temp_file_path.replace("\\", "/")
    temp_file_path = os.path.abspath(temp_file_path)
    return temp_file_path


def read_yaml(path: str):
    with open(path, mode="r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def spath(path: str) -> str:
    if os.path.exists(path):
        return os.path.abspath(path)
    try:
        return locate_path_upwards(path, project_dir)
    except FileNotFoundError:
        pass
    path = path.replace("\\", "/").split("/")[-1]
    for dirpath, dirnames, filenames in os.walk(project_dir):
        for filename in filenames:
            if filename == path:
                return os.path.abspath(os.path.join(dirpath, filename))
    raise FileNotFoundError(f'spath has tried to match and search in the project, but still can not find: {path}')


def locate_path_upwards(relative_path, upper_path: str = project_dir) -> str:
    current_dir = os.getcwd()  # 获取当前工作目录
    tried_dirs = []
    while True:
        file_path = os.path.join(current_dir, relative_path)
        if os.path.exists(file_path):
            return os.path.abspath(str(file_path))
        # 向上一级目录
        current_dir = os.path.dirname(current_dir)
        tried_dirs.append(current_dir)
        # 如果已经到达根目录，则停止搜索
        if current_dir == os.path.dirname(current_dir):
            break
        # 如果达到上界，则停止搜索
        if os.path.abspath(current_dir) == os.path.abspath(upper_path):
            break

    raise FileNotFoundError(f'{tried_dirs}\n尝试了以上的路径，但仍未匹配到该相对路径')


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
