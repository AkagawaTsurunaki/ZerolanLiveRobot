import json
from typing import List

import gradio as gr
import requests

URL = '127.0.0.1:11451'


def res(message: str, history: List[dict]):
    response = requests.get(url=f'http://{URL}/history')
    history: List[dict] = json.loads(response.json())
    if len(history) > 0:
        content = history[-1].get('content')
        return content


chat_interface = gr.ChatInterface(
    fn=res,
    chatbot=gr.Chatbot(height=300),
    textbox=gr.Textbox(placeholder='请输入...', container=False, scale=7),
    title='Zerolan Live Robot Controller Interface',
    description='这里与 Zerolan Live Robot 进行文字对话',
    theme='soft',
    examples=['你好', '你叫什么名字?', '你能干什么?'],
    cache_examples=True,
    retry_btn=None,
    undo_btn='撤回',
    clear_btn='清除'
)

chat_interface.launch()
