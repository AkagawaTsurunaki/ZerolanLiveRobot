import os.path
import sys
import uuid
from dataclasses import asdict, dataclass
from http import HTTPStatus
from urllib.parse import urljoin

import requests
import yaml
from loguru import logger


def load_config():
    """
        检查配置文件是否无误
        :return: 配置字典
    """
    # 读取配置文件

    logger.info('正在读取 GPTSoVITSServiceConfig……')

    if not os.path.exists('gptsovits/config.yaml'):
        logger.critical('配置文件缺失：gptsovits/config.yaml')
        exit()

    with open('gptsovits/config.yaml', mode='r', encoding='utf-8') as file:
        config: dict = yaml.safe_load(file)
        config = config.get('GPTSoVITSServiceConfig', None)

    if not config:
        logger.error('无法读取 GPTSoVITSServiceConfig，格式不正确')

    tmp_dir = config.get('tmp_dir', r'gptsovits\.tmp')
    try:
        if not os.path.exists(tmp_dir):
            os.mkdir(tmp_dir)
            logger.info(f'临时目录创建成功：{tmp_dir}')
    except Exception as e:
        logger.warning(f'配置文件指定的临时目录无法被创建，使用默认临时目录')

    tmp_dir = os.path.abspath(tmp_dir)
    host = config.get('host', '127.0.0.1')
    port = config.get('port', 9880)
    server_url = f"http://{host}:{port}"
    debug = config.get('debug', False)
    clean = config.get('clean', False)

    logger.info('GPT-SoVITS 服务配置文件加载完成')

    return debug, server_url, tmp_dir, clean


debug, server_url, tmp_dir, clean = load_config()


@dataclass
class GPTSoVITSRequest:
    text: str
    text_language: str


@dataclass
class GPTSoVITSChangeRefer:
    refer_wav_path: str
    prompt_text: str
    prompt_language: str


def write_wav(wav_data):
    ran_file_name = uuid.uuid4()
    tmp_wav_file_path = os.path.join(tmp_dir, f'{ran_file_name}.wav')
    with open(file=tmp_wav_file_path, mode='wb') as wav_file:
        wav_file.write(wav_data)
        logger.debug(f'音频文件保存至：{tmp_wav_file_path}')
    tmp_wav_file_path = tmp_wav_file_path.replace("/", "\\")
    return tmp_wav_file_path


def predict(text: str, text_language: str):
    # 检查语言
    assert text_language in ['zh', 'en', 'ja']
    logger.info(f'🤖 [{text_language}] {text}')

    # 将数据发送给GPT-SOVITS 服务器
    req = GPTSoVITSRequest(text, text_language)
    response = requests.post(server_url, json=asdict(req))
    # 请求正常时写入音频
    if response.status_code == HTTPStatus.OK:
        # 将音频文件写入临时目录
        return write_wav(response.content)
    elif response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        return None
    return None


def change_prompt(refer_wav_path: str, prompt_text: str, prompt_language: str):
    """
    修改提示。

    :param refer_wav_path: 参考音频文件路径。
    :param prompt_text: 新的提示内容。
    :param prompt_language: 提示内容的语言，只能是 'zh'（中文）、'en'（英文）或 'ja'（日文）。
    :return: 返回 True 表示修改成功，False 表示修改失败。
    """
    if not os.path.exists(refer_wav_path):
        return False
    if prompt_text is None or prompt_text == '':
        return False
    if not prompt_language in ['zh', 'en', 'ja']:
        return False
    data = GPTSoVITSChangeRefer(refer_wav_path, prompt_text, prompt_language)
    change_prompt_url = urljoin(server_url, '/change_refer')
    response = requests.post(change_prompt_url, json=asdict(data))

    return response.status_code == HTTPStatus.OK and response.json()['code'] == 0
