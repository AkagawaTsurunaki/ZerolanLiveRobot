import dataclasses
import os.path
import uuid
from urllib.parse import urljoin

import requests
from flask import jsonify
from loguru import logger

from common import HttpResponseBody, Code
from gptsovits.common import Config, Request
from gptsovits.service import read_config

# 如果修改了配置文件，那么 server_url 将会被覆盖
server_url = 'http://127.0.0.1:9880'

# 如果修改了配置文件，那么 tmp_dir 将会被覆盖
tmp_dir = './gptsovits/.tmp'


def remove_newlines(text):
    cleaned_text = text.replace('\n', '').replace('\r', '')
    return cleaned_text


def write_wav(wav_data):
    ran_file_name = uuid.uuid4()
    tmp_wav_file_path = os.path.join(tmp_dir, f'{ran_file_name}.wav')
    with open(file=tmp_wav_file_path, mode='wb') as wav_file:
        wav_file.write(wav_data)
        logger.info(f'音频文件保存至：{tmp_wav_file_path}')


def predict(text: str, text_language: str):
    # 检查语言
    assert text_language in ['zh', 'en', 'ja']
    logger.info(f'指定语言：{text_language}')

    # 预先对模型的文段进行清理，删除换行符
    text = remove_newlines(text)
    logger.info(f'合成内容：{text}')

    # 将数据发送给GPT-SOVITS 服务器
    data = dataclasses.asdict(Request(text, text_language))
    response = requests.post(server_url, json=data)

    # 将音频文件写入临时目录
    return write_wav(response.content)


def handle_config():
    config_dict = read_config(default_config_path='./gptsovits/config.json')
    config = Config(**config_dict)

    # 检测路径是否是一个目录
    if not os.path.isdir(config.tmp_dir):
        return jsonify(HttpResponseBody(
            code=Code.PATH_IS_NOT_A_DIR.value,
            msg=f"以下路径不是一个目录：{config.tmp_dir}",
        ))

    # 如果目录不存在，则创建一个
    try:
        if not os.path.exists(config.tmp_dir):
            os.mkdir(config.tmp_dir)
        global tmp_dir
        tmp_dir = config.tmp_dir
        logger.info(f'临时目录创建成功：{config.tmp_dir}')
    except Exception as e:
        tmp_dir = './gptsovits/.tmp'
        logger.warning(f'配置文件指定的临时目录无法被创建，使用默认临时目录')

    # 检查URL
    global server_url
    server_url = urljoin(config.host, ":" + str(config.port))

    return config


if __name__ == '__main__':
    config = handle_config()
