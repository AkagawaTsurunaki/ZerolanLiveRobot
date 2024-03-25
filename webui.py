from typing import List

import gradio as gr
import requests

URL = '127.0.0.1:11451'


def stub(message, history):
    pass


def history():
    response = requests.get(url=f'http://{URL}/history')
    history: List[dict] = response.json()
    history = [item.get('content') for item in history]
    result = []
    if len(history) > 0:
        for i in range(0, len(history), 2):
            result.append((history[i], history[i + 1]))

    return result


def reset():
    response = requests.get(url=f'http://{URL}/reset')
    assert response.status_code == 200, '无法执行命令'


with gr.Blocks(theme=gr.themes.Soft()) as controller_inteface:
    gr.Markdown('# 🕹️ Zerolan Live Robot 中央控制面板')
    with gr.Row():
        gr.Chatbot(label='LLM 对话区', value=history, every=1, height=800, min_width=800)
        with gr.Column():
            gr.Markdown('## 运行时控制')
            reset_button = gr.ClearButton(value='🔃 重载提示词')
            stop_button = gr.ClearButton(value='🫢 停止发声')

            reset_button.click(fn=reset)
        #
        with gr.Column():
            gr.Markdown('## 模型控制')
            btn01 = gr.ClearButton(value='🔃 重载 LLM 服务')
            btn02 = gr.ClearButton(value='🫢 重载 TTS 服务')
            btn03 = gr.ClearButton(value='🫢 重载 TTS 服务')

    # gr.ChatInterface(
    #     fn=stub,
    #     chatbot=gr.Chatbot(label='LLM 对话区', value=res, every=1, height=800, min_width=300),
    #     textbox=gr.Textbox(placeholder='请输入...', container=False, scale=7),
    #     title='Zerolan Live Robot 控制面板',
    #     theme='soft',
    #     retry_btn=None,
    #     undo_btn='撤回',
    #     clear_btn=clr_btn
    # )

controller_inteface.launch()
