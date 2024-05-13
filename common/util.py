import os
import re
import time
from typing import Any, Final
import base64
import io

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
    cur_time_str = time.strftime("%Y%m%d%H%M%S", time.localtime())
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


import PIL.Image


def convert_pil_image_to_base64_str(image: PIL.Image.Image):
    """
    将 PIL.Image.Image 转化为 Base64 字符串
    Reference: https://zhuanlan.zhihu.com/p/629598995
    :return:
    """
    assert isinstance(image, PIL.Image.Image), f'image 必须是 PIL.Image.Image 类型。'
    # 创建一个BytesIO对象，用于临时存储图像数据
    image_data = io.BytesIO()

    # 将图像保存到BytesIO对象中，格式为PNG
    image.save(image_data, format='PNG')

    # 将BytesIO对象的内容转换为字节串
    image_data_bytes = image_data.getvalue()

    # 将图像数据编码为Base64字符串
    encoded_image = base64.b64encode(image_data_bytes).decode('utf-8')

    return encoded_image


def convert_base64_str_to_pil_image(encoded_image: str):
    """
    将 Base64 字符串转化为 PIL.Image.Image
    Reference: https://zhuanlan.zhihu.com/p/629598995
    :param encoded_image:
    :return:
    """
    assert isinstance(encoded_image, str), f'encoded_image 必须是字符串 str 类型。'
    img_data = base64.b64decode(encoded_image)
    img_data = io.BytesIO(img_data)
    # base64解码为PIL图像
    image = PIL.Image.open(img_data).convert("RGB")
    return image
