import json
from dataclasses import dataclass
from typing import List
from loguru import logger

from flask import Flask, jsonify

import vad.service

app = Flask(__name__)

DEBUG = False
HOST = '127.0.0.1'
PORT = 11451
CUSTOM_PROMPT_PATH: str = './template/custom_prompt.json'
HISTORY: List[dict] = []
MAX_HISTORY: int = 40


@dataclass
class ZerolanServiceStatus:
    @dataclass
    class VAD:
        is_alive: bool = True
        pause: bool = False


zerolan_service_status = ZerolanServiceStatus()


@app.route('/vad/switch')
def handle_vad_switch():
    if zerolan_service_status.VAD.pause:
        vad.service.resume()
    else:
        vad.service.pause()
    logger.info(f'🎙️ VAD 服务现在状态: {"" if zerolan_service_status.VAD.pause else ""} ')


def load_custom_history():
    global HISTORY
    with open(file=CUSTOM_PROMPT_PATH, mode='r', encoding='utf-8') as file:
        json_value: dict = json.load(file)
        history = json_value.get('history', [])
        HISTORY = history
        return history


@app.route('/reset', methods=['GET'])
def reset():
    global HISTORY
    HISTORY = load_custom_history()
    return '记忆已被重置'


@app.route('/history', methods=['GET'])
def handle_history():
    return jsonify(get_history())


def get_history():
    global HISTORY
    return HISTORY


def init(debug: bool, host: str, port: int, custom_prompt_path: str):
    global HOST, DEBUG, PORT, CUSTOM_PROMPT_PATH, HISTORY
    DEBUG = debug
    HOST = host
    PORT = port
    CUSTOM_PROMPT_PATH = custom_prompt_path
    HISTORY = load_custom_history()
    return True


def start():
    app.run(host=HOST, port=PORT, debug=DEBUG)


def set_history(history: List[dict]):
    global HISTORY
    HISTORY = history


def try_compress_history():
    # 当历史记录过多时可能会导致 GPU 占用过高
    # 故设计一个常量来检测是否超过阈值
    if len(HISTORY) == 0 or len(HISTORY) > MAX_HISTORY:
        load_custom_history()
