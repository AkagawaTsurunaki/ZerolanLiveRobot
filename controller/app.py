from dataclasses import asdict, dataclass
from typing import List

from flask import Flask, jsonify

import vad.service
from audio_player.service import AudioPlayerService, AudioPlayerStatus
from llm.pipeline import LLMQuery, Chat
from config import GlobalConfig
from lifecycle import LifeCycle
from obs.service import ObsService
from vad.service import VADServiceStatus

_app = Flask(__name__.split('.')[0])

_audio_player_service: AudioPlayerService
_obs_service: ObsService
_lifecycle: LifeCycle

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


def init(cfg: GlobalConfig, lifecycle: LifeCycle,
         audio_player_service: AudioPlayerService,
         obs_service: ObsService):
    global _host, _debug, _port, _audio_player_service, _obs_service, _lifecycle
    _host = cfg.zerolan_live_robot_config.host
    _port = cfg.zerolan_live_robot_config.port
    _debug = cfg.zerolan_live_robot_config.debug
    _audio_player_service = audio_player_service
    _obs_service = obs_service
    _lifecycle = lifecycle


def start():
    _app.run(host=_host, port=_port, debug=_debug)


@_app.route('/memory/reset', methods=['POST'])
def _handle_memory_reset():
    _lifecycle.try_reset_memory(force=True)
    message = 'Memory reset'
    return jsonify(asdict(ControllerResponse(message=message)))


@_app.route('/memory/fetch', methods=['GET'])
def _handle_memory_fetch():
    memory: LLMQuery = _lifecycle.memory()
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
    _audio_player_service.pause()
    message = 'Audio player service paused.'
    return jsonify(asdict(ControllerResponse(message=message)))


@_app.route('/audio-player/resume', methods=['POST'])
def _handle_audio_player_resume():
    _audio_player_service.resume()
    message = 'Audio player service resumed.'
    return jsonify(asdict(ControllerResponse(message=message)))


@_app.route('/audio-player/status', methods=['POST'])
def _handle_audio_player_status():
    status = _audio_player_service.status()
    message = f'Audio player status: {status}'
    return jsonify(asdict(AudioPlayerControlResponse(message=message, status=status)))


@_app.route('/obs/clear', methods=['POST'])
def _handle_obs_clear():
    _obs_service.clear_output()
    message = 'OBS subtitle cleared.'
    return jsonify(asdict(ControllerResponse(message=message)))
