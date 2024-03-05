import json
from dataclasses import dataclass
from enum import Enum
import psutil

import chatglm3.common


class Code(Enum):
    OK = 0
    PORT_IS_ALREADY_USED = 100
    PATH_DOSE_NOT_EXIST = 101
    BLANK_STRING = 102
    INVALID_NUMBER = 103
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
    if s is '':
        return True
    if "".isspace():
        return True
    return False
