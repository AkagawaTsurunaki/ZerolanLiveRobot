import os.path
from dataclasses import asdict

from flask import Flask, request, jsonify
from funasr import AutoModel
from loguru import logger

from utils.datacls import HTTPResponseBody

# 推理模型
MODEL: AutoModel

app = Flask(__name__)


def _predict(wav_path) -> str | None:
    try:
        res = MODEL.generate(input=wav_path,
                             batch_size_s=300,
                             hotword='魔搭')
        res = res[0]['text']
        return res
    except Exception as e:
        logger.exception(e)
        return None


@app.route('/asr/predict', methods=['GET', 'POST'])
def handle_predict():
    req = request.json
    wav_path = req.get('wav_path', None)
    if not os.path.exists(wav_path):
        response = HTTPResponseBody(ok=False, msg='无法找到音频路径')
        return jsonify(asdict(response))
    transcript = _predict(wav_path)
    response = HTTPResponseBody(ok=True, msg='推理成功', data={'transcript': transcript})
    return jsonify(asdict(response))


def start(model_path, host, port, debug, version="v2.0.4"):
    global MODEL
    logger.info('👂️ Auto speech recognition service initializing...')
    MODEL = AutoModel(model=model_path, model_revision=version)
    logger.info(f'👂️ Auto speech recognition model {model_path} loaded.')
    app.run(host=host, port=port, debug=debug)
