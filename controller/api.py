from http import HTTPStatus

import gradio
import requests
from loguru import logger

from utils.datacls import HTTPResponseBody

URL = 'http://127.0.0.1:11451'


def obs_clear():
    try:
        response = requests.post(url=f'{URL}/obs/clear')
        assert response.status_code == HTTPStatus.OK
        response = HTTPResponseBody(**response.json())
        assert response.ok
        gradio.Info(response.msg)
    except Exception as e:
        logger.exception(e)
        gradio.Error('无法清空 OBS 输出')
