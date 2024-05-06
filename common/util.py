import os
import re
import time
from typing import Any, Final

from zio.util import save_json

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


def urljoin(host: str, port: int, path: str = None, protocol: str = 'http'):
    assert host and port and protocol
    assert isinstance(host, str) and isinstance(port, int) and isinstance(protocol, str)
    assert protocol in ['http', 'https'], f'Unsupported protocol.'

    url = f"{protocol}://{host}:{port}"
    if path:
        assert isinstance(path, str)
        assert path[0] == '/', f'"path" should begin with "/".'
        url += path

    return url


def save(dir: str | os.PathLike, obj: Any):
    cur_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    save_path = os.path.join(dir, cur_time_str)
    save_json(save_path, obj)


def is_english_string(input_string):
    if not input_string:
        return False
    # 正则表达式匹配英文字符、数字、空格和标点符号
    pattern = r'^[a-zA-Z0-9\s\.,;:!?]*$'
    # 使用re.match()函数检查输入字符串是否匹配正则表达式
    if re.match(pattern, input_string):
        return True
    else:
        return False


def try_mkdir(directory: str):
    flag = input(f'Directory "{directory}" does not exist, should we create it? [y]/n')
    if 'n' == flag:
        return
    os.makedirs(directory)
