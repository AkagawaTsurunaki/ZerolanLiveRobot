from dataclasses import asdict, dataclass
from typing import List

from flask import Flask, jsonify

from obs.api import ObsService
from vad.service import VADService, VADServiceStatus
from audio_player.service import AudioPlayerService, AudioPlayerStatus
from common.abs_app import AbstractApp
from config import GlobalConfig
from lifecycle import LifeCycle
from utils.datacls import Chat, LLMQuery

app = Flask(__name__.splits('.')[0])


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


class ControllerApp(AbstractApp):

    def __init__(self, cfg: GlobalConfig, lifecycle: LifeCycle,
                 audio_player_service: AudioPlayerService,
                 vad_service: VADService,
                 obs_service: ObsService):
        super().__init__()
        self._host = cfg.zerolan_live_robot_config.host
        self._port = cfg.zerolan_live_robot_config.port
        self._debug = cfg.zerolan_live_robot_config.debug
        self._lifecycle: LifeCycle = lifecycle
        self._audio_player_service = audio_player_service
        self._vad_service = vad_service
        self._obs_service = obs_service

    def start(self):
        app.run(host=self._host, port=self._port, debug=self._debug)

    @app.route('/memory/reset', methods=['POST'])
    def reset(self):
        self._lifecycle.try_reset_memory(force=True)
        message = 'Memory reset'
        return jsonify(asdict(ControllerResponse(message=message)))

    @app.route('/memory/fetch', methods=['GET'])
    def handle_history(self):
        memory: LLMQuery = self._lifecycle.memory()
        message = f'{len(memory.history)} conversations.'
        response = MemoryControlResponse(message=message, history=memory.history)
        return jsonify(asdict(response))

    @app.route('/vad/pause', methods=['POST'])
    def handle_vad_switch(self):
        self._vad_service.pause()
        message = 'VAD service paused.'
        return jsonify(asdict(ControllerResponse(message=message)))

    @app.route('/vad/resume', methods=['POST'])
    def handle_vad_switch(self):
        self._vad_service.resume()
        message = 'VAD service resumed.'
        return jsonify(asdict(ControllerResponse(message=message)))

    @app.route('/vad/status', methods=['POST'])
    def handle_vad_switch(self):
        status = self._vad_service.status()
        message = f'VAD service status: {status}'
        return jsonify(asdict(VADControlResponse(message=message, status=status)))

    @app.route('/audio-player/pause', methods=['POST'])
    def handle_audio_player_pause(self):
        self._audio_player_service.pause()
        message = 'Audio player service paused.'
        return jsonify(asdict(ControllerResponse(message=message)))

    @app.route('/audio-player/resume', methods=['POST'])
    def handle_audio_player_resume(self):
        self._audio_player_service.resume()
        message = 'Audio player service resumed.'
        return jsonify(asdict(ControllerResponse(message=message)))

    @app.route('/audio-player/status', methods=['POST'])
    def handle_audio_player_status(self):
        status = self._audio_player_service.status()
        message = f'Audio player status: {status}'
        return jsonify(asdict(AudioPlayerControlResponse(message=message, status=status)))

    @app.route('/obs/clear', methods=['POST'])
    def handle_obs_clear(self):
        self._obs_service.clear_output()
        message = 'OBS subtitle cleared.'
        return jsonify(asdict(ControllerResponse(message=message)))
