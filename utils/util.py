import json
import math
import os
import time
from typing import Any, Final

import psutil

# 这个常数记录了模块被第一次导入时的时间, 这个数值此后不会再发生变化
# 在Windows系统中，文件名不允许使用的字符有： < > / \ | : " * ?
SERVICE_START_TIME: Final[str] = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())


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


def save_service(service_name: str, obj: Any, tmp_dir='.tmp'):
    """
    根据服务名和默认临时文件夹生成服务存档
    :param service_name: 服务名
    :param obj: 服务内部的数据
    :param tmp_dir: 临时文件夹路径
    """
    if obj is not None:
        save_dir = os.path.join(tmp_dir, service_name)
        # .tmp/{service_name}
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)
        # .tmp/{service_name}/{SERVICE_START_TIME}.json
        assert os.path.exists(save_dir)
        save_path = os.path.join(save_dir, f'{SERVICE_START_TIME}.json')
        with open(file=save_path, mode='w+', encoding='utf-8') as file:
            json.dump(fp=file, obj=obj, ensure_ascii=False)


def is_port_in_use(port):
    """
    检查指定端口是否被占用
    :param port: int, 待检查的端口号
    :return: bool, 如果端口被占用返回 True，否则返回 False
    """
    for proc in psutil.process_iter():
        for con in proc.connections():
            if con.status == 'LISTEN' and con.laddr.port == port:
                return True
    return False


def time_stamp_diff_sec(ts1: int, ts2: int):
    return math.fabs(ts1 - ts2) / 1000.


def read_json(path: str | os.PathLike) -> Any:
    assert os.path.exists(path)
    with open(file=path, encoding='utf-8', mode='r') as file:
        return json.load(file)
