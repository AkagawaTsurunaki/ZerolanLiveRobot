import os.path

from flask import Flask, request, jsonify
from funasr import AutoModel
from loguru import logger

from common.abs_app import AbstractApp
from config import ASRConfig

app = Flask(__name__)


class SpeechParaformerApp(AbstractApp):

    def __init__(self, cfg: ASRConfig):
        super().__init__()
        self._model_path = cfg.models[0].model_path
        self._version = cfg.models[0].version
        self._host = cfg.host
        self._port = cfg.port
        self._debug = cfg.debug
        logger.info('👂️ Auto speech recognition service initializing...')
        self._model = AutoModel(model=self._model_path, model_revision=self._version)
        logger.info(f'👂️ Auto speech recognition model {self._model_path} loaded.')

    def start(self):
        app.run(host=self._host, port=self._port, debug=self._debug)

    @app.route('/asr/predict', methods=['GET', 'POST'])
    def handle_predict(self):
        req = request.json
        wav_path = req.get('wav_path', None)
        assert os.path.exists(wav_path), f'Can not find wav file path: "{wav_path}"'
        transcript = self._predict(wav_path)
        return jsonify({'transcript': transcript})

    def _predict(self, wav_path) -> str | None:
        try:
            res = self._model.generate(input=wav_path,
                                       batch_size_s=300,
                                       hotword='魔搭')
            res = res[0]['text']
            return res
        except Exception as e:
            logger.exception(e)
            return None
