from dataclasses import asdict, dataclass
import os.path
import uuid

import requests
from loguru import logger

from gptsovits import SERVER_URL, TMP_DIR


@dataclass
class GPTSoVITSRequest:
    text: str
    text_language: str


def write_wav(wav_data):
    ran_file_name = uuid.uuid4()
    tmp_wav_file_path = os.path.join(TMP_DIR, f'{ran_file_name}.wav')
    with open(file=tmp_wav_file_path, mode='wb') as wav_file:
        wav_file.write(wav_data)
        logger.debug(f'音频文件保存至：{tmp_wav_file_path}')
    tmp_wav_file_path = tmp_wav_file_path.replace("/", "\\")
    return tmp_wav_file_path


async def predict(text: str, text_language: str):
    # 检查语言
    assert text_language in ['zh', 'en', 'ja']
    logger.info(f'[{text_language}] {text}')

    # 将数据发送给GPT-SOVITS 服务器
    data_dict = asdict(GPTSoVITSRequest(text, text_language))
    response = requests.post(SERVER_URL, json=data_dict)

    # 将音频文件写入临时目录
    return write_wav(response.content)
