from dataclasses import asdict

from flask import Flask, jsonify

import initzr
import lifecircle
import obs.api
import vad.service
from utils.datacls import HTTPResponseBody

app = Flask(__name__)


@app.route('/vad/switch', methods=['POST'])
def handle_vad_switch():
    resume = vad.service.switch()
    msg = '已启用听觉' if resume else '已禁用听觉'
    response = HTTPResponseBody(ok=True, msg=msg, data={'vad': resume})
    return jsonify(asdict(response))


@app.route('/llm/reset', methods=['GET'])
def reset():
    lifecircle.try_reset_memory(force=True)
    return 'OK'


@app.route('/history', methods=['GET'])
def handle_history():
    return jsonify()


@app.route('/audio_player/switch', methods=['POST'])
def handle_audio_player_switch():
    raise NotImplementedError('resume = audio_player.service.switch()')
    # resume = audio_player.service.switch()
    # msg = '已启用发声' if resume else '已禁用发声'
    # response = HTTPResponseBody(ok=True, msg=msg, data={'audio_player': resume})
    # return jsonify(asdict(response))


@app.route('/obs/clear', methods=['POST'])
def handle_obs_clear():
    obs.api.write_llm_output('')
    obs.api.write_tone_output(None)
    obs.api.write_danmaku_output(None)
    response = HTTPResponseBody(ok=True, msg='已清除 OBS 输出')
    return jsonify(asdict(response))


def start():
    config = initzr.load_zerolan_live_robot_config()
    app.run(host=config.host, port=config.port, debug=config.debug)
