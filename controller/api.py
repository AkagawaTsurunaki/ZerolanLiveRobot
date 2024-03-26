from http import HTTPStatus
from typing import List

import gradio
import requests
from loguru import logger

import initzr
from utils.datacls import HTTPResponseBody

URL = 'http://127.0.0.1:11451'


def init():
    global URL
    g_config = initzr.load_global_config()
    _, host, port, _ = initzr.load_zerolan_live_robot_config(g_config)
    URL = f'http://{host}:{port}'


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


def audio_player_switch():
    try:
        response = requests.post(url=f'{URL}/audio_player/switch')
        assert response.status_code == HTTPStatus.OK
        response = HTTPResponseBody(**response.json())
        assert response.ok
        gradio.Info(message=response.msg)
    except Exception as e:
        logger.exception(e)
        gradio.Error(message='无法启用或禁用发声')


def get_history():
    try:
        response = requests.get(url=f'{URL}/history')
        history: List[dict] = response.json()
        history = [item.get('content') for item in history]
        result = []
        if len(history) > 0:
            for i in range(0, len(history), 2):
                result.append((history[i], history[i + 1]))
        return result
    except Exception as e:
        logger.exception(e)
        gradio.Error('获取历史对话失败')
        return []


def llm_reset():
    response = requests.get(url=f'{URL}/llm/reset')
    assert response.status_code == 200, '无法执行命令'


def vad_switch():
    try:
        response = requests.post(url=f'{URL}/vad/switch')
        assert response.status_code == HTTPStatus.OK
        response = HTTPResponseBody(**response.json())
        assert response.ok
        gradio.Info(message=response.msg)
    except Exception as e:
        logger.exception(e)
        gradio.Error(message='无法启用或禁用听觉')


init()
