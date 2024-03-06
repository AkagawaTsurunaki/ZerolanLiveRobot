import json
import os
from dataclasses import dataclass
from enum import Enum

import psutil
import requests


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
    data = None







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


def remove_newlines(text):
    cleaned_text = text.replace('\n', '').replace('\r', '')
    return cleaned_text





