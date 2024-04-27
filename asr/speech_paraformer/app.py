import os.path

from flask import Flask, request, jsonify
from funasr import AutoModel
from loguru import logger

from config import GlobalConfig

# Global attributes
_app = Flask(__name__)  # Flask application instance

# Initialize global variables
_host: str  # Host address for the Flask application
_port: int  # Port number for the Flask application
_debug: bool  # Debug mode flag for the Flask application
_model: any  # ASR model for recognize speeches


def init(cfg: GlobalConfig):
    global _host, _port, _debug, _model
    asr_cfg = cfg.auto_speech_recognition
    model_path = asr_cfg.models[0].model_path
    version = asr_cfg.models[0].version
    _host = asr_cfg.host
    _port = asr_cfg.port
    _debug = asr_cfg.debug
    logger.info('👂️ Auto speech recognition service initializing...')
    _model = AutoModel(model=model_path, model_revision=version)
    logger.info(f'👂️ Auto speech recognition model {model_path} loaded.')


def start():
    _app.run(host=_host, port=_port, debug=_debug)


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
