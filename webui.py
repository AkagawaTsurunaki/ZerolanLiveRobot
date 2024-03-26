from http import HTTPStatus
from typing import List

import gradio
import gradio as gr
import requests
from loguru import logger

from utils.datacls import HTTPResponseBody

URL = 'http://127.0.0.1:11451'


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


with gr.Blocks(theme=gr.themes.Soft()) as controller_inteface:
    gr.Markdown('# 🕹️ Zerolan Live Robot ver1.1 控制面板')
    with gr.Row():
        gr.Chatbot(label='LLM 对话区', value=get_history, every=1, height=800, min_width=800)

        with gr.Column():
            gr.Markdown('## 运行时控制')
            llm_reset_button = gr.ClearButton(value='🔃 重载提示词')
            audio_player_switch_btn = gr.ClearButton(value='👄 启禁用发声')
            vad_switch_btn = gr.Button(value='👂️ 启禁用听觉')
            # stop_zerolan_button = gr.Button(value='⛔️ 终止 Zerolan Live Robot')

            llm_reset_button.click(fn=llm_reset)
            audio_player_switch_btn.click(fn=audio_player_switch)
            vad_switch_btn.click(fn=vad_switch)

        #
        with gr.Column():
            gr.Markdown('## 模型控制')
            btn01 = gr.ClearButton(value='???')
            btn02 = gr.ClearButton(value='???')
            btn03 = gr.ClearButton(value='???')

controller_inteface.launch()
