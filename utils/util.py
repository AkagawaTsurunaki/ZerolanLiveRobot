import json
import os
import time
from typing import Any


def is_blank(s: str):
    """
    判断字符串是否为空字符串
    :param s: 待判断的字符串
    :return: 如果字符串为空返回 True，否则返回 False
    """
    if s is None:
        return True
    if s == '':
        return True
    if "".isspace():
        return True
    return False


def is_valid_port(port):
    try:
        port = int(port)
        if 0 < port < 65536:
            return True
        else:
            return False
    except ValueError:
        return False


def url_join(host, port, protocol='http'):
    if not host or not port or not protocol:
        return None

    if protocol not in ['http']:
        return None

    url = f"{protocol}://{host}:{port}"
    return url


def create_file_if_not_exists(file_path):
    # 获取目录路径
    dir_path = os.path.dirname(file_path)

    # 创建目录及父级目录
    os.makedirs(dir_path, exist_ok=True)

    # 创建文件
    with open(file=file_path, mode='w', encoding='utf-8') as f:
        f.write("")


def save_json(file_path: str | os.PathLike, obj: Any):
    """
    保存 JSON 文件。如果目录不存在会自动创建。
    :param file_path: 目标文件路径。
    :param obj: 将被转换为 JSON 的对象
    :return:
    """
    dir_path = os.path.dirname(file_path)
    os.makedirs(dir_path, exist_ok=True)
    with open(file=file_path, mode='w+', encoding='utf-8') as file:
        json.dump(fp=file, obj=obj)


def save(dir: str | os.PathLike, obj: Any):
    cur_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    save_path = os.path.join(dir, cur_time_str)
    save_json(save_path, obj)
