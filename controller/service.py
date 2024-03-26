import json
from dataclasses import asdict
from typing import List

from flask import Flask, jsonify

import asr.service
import audio_player.service
import vad.service
from utils.datacls import HTTPResponseBody, ZerolanServiceStatus, VAD

app = Flask(__name__)

DEBUG = False
HOST = '127.0.0.1'
PORT = 11451
CUSTOM_PROMPT_PATH: str = './template/custom_prompt.json'
g_history: List[dict] = []
MAX_HISTORY: int = 40

zss = ZerolanServiceStatus(
    vad_service=VAD(pause=False, is_alive=True)
)


def _vad_switch():
    if zss.vad_service.pause:
        vad.service.resume()
    else:
        vad.service.pause()
    zss.vad_service.pause = not zss.vad_service.pause


@app.route('/vad/switch', methods=['POST'])
def handle_vad_switch():
    _vad_switch()
    vad_status_str = '已暂停' if zss.vad_service.pause else '已继续'
    response = HTTPResponseBody(ok=True, msg=f'VAD 服务{vad_status_str}', data=zss)
    return jsonify(asdict(response))


def _load_custom_history():
    global g_history
    with open(file=CUSTOM_PROMPT_PATH, mode='r', encoding='utf-8') as file:
        json_value: dict = json.load(file)
        g_history = json_value.get('history', [])


@app.route('/llm/reset', methods=['GET'])
def reset():
    _load_custom_history()
    return 'OK'


def get_history() -> List[dict]:
    global g_history
    return g_history


def set_history(history: List[dict]):
    global g_history
    g_history = history


def try_compress_history():
    # 当历史记录过多时可能会导致 GPU 占用过高
    # 故设计一个常量来检测是否超过阈值
    if len(g_history) == 0 or len(g_history) > MAX_HISTORY:
        _load_custom_history()


@app.route('/history', methods=['GET'])
def handle_history():
    return jsonify(get_history())


def init(debug: bool, host: str, port: int, custom_prompt_path: str) -> bool:
    global HOST, DEBUG, PORT, CUSTOM_PROMPT_PATH
    DEBUG = debug
    HOST = host
    PORT = port
    CUSTOM_PROMPT_PATH = custom_prompt_path
    _load_custom_history()
    return True


def start():
    app.run(host=HOST, port=PORT, debug=DEBUG)
