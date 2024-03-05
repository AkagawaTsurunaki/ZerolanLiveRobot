import json
import os
from dataclasses import dataclass
from enum import Enum
import psutil
import requests

import chatglm3.common


class Code(Enum):
    OK = 0
    PORT_IS_ALREADY_USED = 100
    PATH_DOSE_NOT_EXIST = 101
    BLANK_STRING = 102
    INVALID_NUMBER = 103
    PATH_IS_NOT_A_DIR = 104
    ERROR = 500


@dataclass
class HttpResponseBody:
    code: int
    msg: str
    data: chatglm3.common.ModelResponse | chatglm3.common.ModelRequest = None


class CodeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        return json.JSONEncoder.default(self, obj)


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


def check_url_accessible(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.exceptions.RequestException:
        return False


def get_absolute_path(file_name):
    # 获取当前工作目录
    current_dir = os.getcwd()

    # 拼接文件的绝对路径
    absolute_path = os.path.join(current_dir, file_name)

    return absolute_path
