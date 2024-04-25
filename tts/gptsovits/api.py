import os.path
import uuid
from dataclasses import asdict
from http import HTTPStatus
from urllib.parse import urljoin

import requests
from loguru import logger

import initzr
from utils.datacls import GPTSoVITSChangeRefer, GPTSoVITSRequest

CONFIG = initzr.load_gpt_sovits_config()
SERVER_URL = CONFIG.url()
SAVE_DIR = CONFIG.save_dir


def _write_wav(wav_data):
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
        return _write_wav(response.content)
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
        return _write_wav(response.content)
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
