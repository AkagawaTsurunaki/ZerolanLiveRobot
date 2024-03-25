import json
from typing import List

import gradio as gr
import requests

URL = '127.0.0.1:11451'


def res():
    # def inner():
    #     now = datetime.now()
    #     current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    #     return [(f"欢迎使用,当前时间是: {current_time}", 'asdasd')]
    # def inner():
    #
    response = requests.get(url=f'http://{URL}/history')
    history: List[dict] = json.loads(response.json())
    if len(history) > 0:
        history = [item.get('content') for item in history]
        return history


with gr.Blocks() as demo:
    gr.Markdown("# Gradio实时输出的实现")
    gr.Chatbot(value=res, every=1)
    # out_1 = gr.Textbox(label="实时状态",
    #                    value=current_time(),
    #                    every=1,
    #                    info="当前时间", )

demo.launch()

#
# chat_interface = gr.ChatInterface(
#     fn=res,
#     chatbot=gr.Chatbot(height=300),
#     textbox=gr.Textbox(placeholder='请输入...', container=False, scale=7),
#     title='Zerolan Live Robot Controller Interface',
#     description='这里与 Zerolan Live Robot 进行文字对话',
#     theme='soft',
#     examples=['你好', '你叫什么名字?', '你能干什么?'],
#     cache_examples=True,
#     retry_btn=None,
#     undo_btn='撤回',
#     clear_btn='清除'
# )
#
# chat_interface.launch()
# chat_interface.call_function()
