from dataclasses import asdict, dataclass
from typing import List

from flask import Flask, jsonify

import audio_player.service
import lifecycle
import obs.api
import vad.service
from common.datacls import AudioPlayerStatus, VADServiceStatus, Chat, LLMQuery
from config import GLOBAL_CONFIG as G_CFG

_app = Flask(__name__.split('.')[0])

_host: str  # Host address for the Flask application
_port: int  # Port number for the Flask application
_debug: bool  # Debug mode flag for the Flask application


@dataclass
class ControllerResponse:
    message: str


@dataclass
class MemoryControlResponse(ControllerResponse):
    history: List[Chat]


@dataclass
class AudioPlayerControlResponse(ControllerResponse):
    status: AudioPlayerStatus


@dataclass
class VADControlResponse(ControllerResponse):
    status: VADServiceStatus


def init():
    global _host, _debug, _port
    _host = G_CFG.zerolan_live_robot_config.host
    _port = G_CFG.zerolan_live_robot_config.port
    _debug = G_CFG.zerolan_live_robot_config.debug


def start():
    _app.run(host=_host, port=_port, debug=_debug)


@_app.route('/memory/reset', methods=['POST'])
def _handle_memory_reset():
    lifecycle.try_reset_memory(force=True)
    message = 'Memory reset'
    return jsonify(asdict(ControllerResponse(message=message)))


@_app.route('/memory/fetch', methods=['GET'])
def _handle_memory_fetch():
    memory: LLMQuery = lifecycle.memory()
    message = f'{len(memory.history)} conversations.'
    response = MemoryControlResponse(message=message, history=memory.history)
    return jsonify(asdict(response))


@_app.route('/vad/pause', methods=['POST'])
def _handle_vad_pause():
    vad.service.pause()
    message = 'VAD service paused.'
    return jsonify(asdict(ControllerResponse(message=message)))


@_app.route('/vad/resume', methods=['POST'])
def _handle_vad_resume():
    vad.service.resume()
    message = 'VAD service resumed.'
    return jsonify(asdict(ControllerResponse(message=message)))


@_app.route('/vad/status', methods=['POST'])
def _handle_vad_status():
    status = vad.service.status()
    message = f'VAD service status: {status}'
    return jsonify(asdict(VADControlResponse(message=message, status=status)))


@_app.route('/audio-player/pause', methods=['POST'])
def _handle_audio_player_pause():
    audio_player.service.pause()
    message = 'Audio player service paused.'
    return jsonify(asdict(ControllerResponse(message=message)))


@_app.route('/audio-player/resume', methods=['POST'])
def _handle_audio_player_resume():
    audio_player.service.resume()
    message = 'Audio player service resumed.'
    return jsonify(asdict(ControllerResponse(message=message)))


@_app.route('/audio-player/status', methods=['POST'])
def _handle_audio_player_status():
    status = audio_player.service.status()
    message = f'Audio player status: {status}'
    return jsonify(asdict(AudioPlayerControlResponse(message=message, status=status)))


@_app.route('/obs/clear', methods=['POST'])
def _handle_obs_clear():
    obs.api.clear_output()
    message = 'OBS subtitle cleared.'
    return jsonify(asdict(ControllerResponse(message=message)))
