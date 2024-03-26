import json
from dataclasses import asdict
from typing import List

from flask import Flask, jsonify

import audio_player.service
import initzr
import obs.service
import vad.service
from config.global_config import ZerolanLiveRobotConfig
from utils.datacls import HTTPResponseBody

app = Flask(__name__)

CUSTOM_PROMPT_PATH: str = './template/custom_prompt.json'
g_history: List[dict] = []
MAX_HISTORY: int = 40


@app.route('/vad/switch', methods=['POST'])
def handle_vad_switch():
    resume = vad.service.switch()
    msg = '已启用听觉' if resume else '已禁用听觉'
    response = HTTPResponseBody(ok=True, msg=msg, data={'vad': resume})
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


@app.route('/audio_player/switch', methods=['POST'])
def handle_audio_player_switch():
    resume = audio_player.service.switch()
    msg = '已启用发声' if resume else '已禁用发声'
    response = HTTPResponseBody(ok=True, msg=msg, data={'audio_player': resume})
    return jsonify(asdict(response))


@app.route('/obs/clear', methods=['POST'])
def handle_obs_clear():
    obs.service.write_llm_output('')
    obs.service.write_tone_output(None)
    obs.service.write_danmaku_output(None)
    response = HTTPResponseBody(ok=True, msg='已清除 OBS 输出')
    return jsonify(asdict(response))


def _init(config: ZerolanLiveRobotConfig) -> bool:
    global CUSTOM_PROMPT_PATH
    CUSTOM_PROMPT_PATH = config.custom_prompt_path
    _load_custom_history()
    return True


def start():
    config = initzr.load_zerolan_live_robot_config()
    _init(config)
    app.run(host=config.host, port=config.port, debug=config.debug)
