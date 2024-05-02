import os.path

from flask import Flask, request, jsonify
from funasr import AutoModel
from loguru import logger
from common.datacls import ModelNameConst as MNC
from config import GLOBAL_CONFIG as G_CFG

# Global attributes
_app = Flask(__name__)  # Flask application instance

# Initialize global variables
_host: str  # Host address for the Flask application
_port: int  # Port number for the Flask application
_debug: bool  # Debug mode flag for the Flask application
_model: any  # ASR model for recognize speeches


def init():
    logger.info(f'👂️ Application {MNC.PARAFORMER} is initializing...')
    global _host, _port, _debug, _model

    asr_cfg = G_CFG.auto_speech_recognition
    model_path, version = asr_cfg.models[0].model_path, asr_cfg.models[0].version
    _host, _port, _debug = asr_cfg.host, asr_cfg.port, asr_cfg.debug

    logger.info(f'👂️ Model {MNC.PARAFORMER} is loading...')
    _model = AutoModel(model=model_path, model_revision=version)
    assert _model, f'❌️ Model {MNC.BLIP} failed to load.'
    logger.info(f'👂️ Model {MNC.PARAFORMER} loaded successfully.')

    logger.info(f'👂️ Application {MNC.PARAFORMER} initialized successfully.')


def start():
    logger.info(f'👂️ Application {MNC.PARAFORMER} is starting...')
    _app.run(host=_host, port=_port, debug=_debug)
    logger.warning(f'⚠️ Application {MNC.PARAFORMER} stopped.')


def _predict(wav_path) -> str | None:
    try:
        res = _model.generate(input=wav_path,
                              batch_size_s=300,
                              hotword='魔搭')
        res = res[0]['text']
        return res
    except Exception as e:
        logger.exception(e)
        return None


@_app.route('/asr/predict', methods=['GET', 'POST'])
def handle_predict():
    req = request.json
    wav_path = req.get('wav_path', None)
    assert os.path.exists(wav_path), f'Can not find wav file path: "{wav_path}"'
    transcript = _predict(wav_path)
    return jsonify({'transcript': transcript})
