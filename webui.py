from http import HTTPStatus
from typing import List

import gradio
import gradio as gr
import requests

from utils.datacls import parse_http_response_body

URL = 'http://127.0.0.1:11451'


def get_history():
    response = requests.get(url=f'{URL}/history')
    history: List[dict] = response.json()
    history = [item.get('content') for item in history]
    result = []
    if len(history) > 0:
        for i in range(0, len(history), 2):
            result.append((history[i], history[i + 1]))

    return result


def llm_reset():
    response = requests.get(url=f'{URL}/llm/reset')
    assert response.status_code == 200, '无法执行命令'


def vad_switch():
    response = requests.post(url=f'{URL}/vad/switch')
    if response.status_code == HTTPStatus.OK:
        response = parse_http_response_body(response.json())

        if response.ok:
            btn_val = '👂️ 恢复听觉' if response.data.vad_service.pause else '👂️ 关闭听觉'
            gradio.Info(message=response.msg)
    gradio.Error(message='VAD 服务未响应')


with gr.Blocks(theme=gr.themes.Soft()) as controller_inteface:
    gr.Markdown('# 🕹️ Zerolan Live Robot 中央控制面板')
    with gr.Row():
        gr.Chatbot(label='LLM 对话区', value=get_history, every=1, height=800, min_width=800)

        with gr.Column():
            gr.Markdown('## 运行时控制')
            reset_button = gr.ClearButton(value='🔃 重载提示词')
            stop_voice_button = gr.ClearButton(value='👄 开启/关闭语音系统')
            pause_or_resume_vad_button = gr.Button(value='👂️ 开启/关闭听觉系统')

            reset_button.click(fn=llm_reset)
            pause_or_resume_vad_button.click(fn=vad_switch)

        #
        with gr.Column():
            gr.Markdown('## 模型控制')
            btn01 = gr.ClearButton(value='🔃 重载 LLM 服务')
            btn02 = gr.ClearButton(value='🫢 重载 TTS 服务')
            btn03 = gr.ClearButton(value='🫢 重载 TTS 服务')

controller_inteface.launch()
