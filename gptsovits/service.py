import os.path
import uuid
from dataclasses import asdict, dataclass
from http import HTTPStatus
from urllib.parse import urljoin

import requests
from loguru import logger

IS_INITIALIZED = False

DEBUG = False
SERVER_URL = 'http://127.0.0.1:9880'
SAVE_DIR = '.tmp/wav_output'

def check_alive():
    try:
        requests.head(SERVER_URL, timeout=5).status_code
    except Exception as e:
        raise ConnectionError(f'❌️ GPT-SoVTIS 服务无法连接至 {SERVER_URL}')

def init(debug, host, port, save_dir):
    logger.info('👄 GPT-SoVITS 服务初始化中……')
    global DEBUG, SERVER_URL, SAVE_DIR, IS_INITIALIZED
    DEBUG = debug
    SAVE_DIR = save_dir
    SERVER_URL = f"http://{host}:{port}"
    check_alive()
    IS_INITIALIZED = True
    logger.info('👄 GPT-SoVITS 服务初始化完毕')
    return IS_INITIALIZED


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
    tmp_wav_file_path = os.path.join(SAVE_DIR, f'{ran_file_name}.wav')
    with open(file=tmp_wav_file_path, mode='wb') as wav_file:
        wav_file.write(wav_data)
        logger.debug(f'音频文件保存至：{tmp_wav_file_path}')
    tmp_wav_file_path = tmp_wav_file_path.replace("/", "\\")
    return tmp_wav_file_path


def predict(text: str, text_language: str):
    # 检查语言
    assert text_language in ['zh', 'en', 'ja']
    # 将数据发送给GPT-SOVITS 服务器
    req = GPTSoVITSRequest(text, text_language)
    response = requests.post(SERVER_URL, json=asdict(req))
    # 请求正常时写入音频
    if response.status_code == HTTPStatus.OK:
        # 将音频文件写入临时目录
        return write_wav(response.content)
    elif response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        return None
    return None


def predict_with_prompt(text: str, text_language: str, refer_wav_path: str, prompt_text: str, prompt_language: str):
    req = {
        "refer_wav_path": refer_wav_path,
        "prompt_text": prompt_text,
        "prompt_language": prompt_language,
        "text": text,
        "text_language": text_language,
    }
    response = requests.post(SERVER_URL, json=req)
    if response.status_code == HTTPStatus.OK:
        # 将音频文件写入临时目录
        return write_wav(response.content)
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
    change_prompt_url = urljoin(SERVER_URL, '/change_refer')
    response = requests.post(change_prompt_url, json=asdict(data))

    return response.status_code == HTTPStatus.OK and response.json()['code'] == 0
