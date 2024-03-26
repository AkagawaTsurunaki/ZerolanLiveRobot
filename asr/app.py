import os.path
from dataclasses import asdict

from flask import Flask, request, jsonify
from funasr import AutoModel
from loguru import logger

import initzr
from config.global_config import ASRConfig
from utils.datacls import HTTPResponseBody

# 推理模型
MODEL: AutoModel

app = Flask(__name__)


def _init(config: ASRConfig):
    global MODEL
    if config.vad_model_path:
        logger.warning('⚠️ 使用 VAD 模型可能会出现疑难杂症，建议不要使用')
    MODEL = AutoModel(model=config.speech_model_path, model_revision="v2.0.4",
                      # vad_model=vad_model_path, vad_model_revision="v2.0.4",
                      # punc_model="ct-punc-c", punc_model_revision="v2.0.4",
                      # spk_model="cam++", spk_model_revision="v2.0.2",
                      )
    logger.info('👂️ 自动语音识别服务初始化完毕')


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


@app.route('/asr/predict', methods=['GET'])
def handle_predict():
    req = request.json
    wav_path = req.get('wav_path', None)
    if not os.path.exists(wav_path):
        response = HTTPResponseBody(ok=False, msg='无法找到音频路径')
        return jsonify(asdict(response))
    transcript = _predict(wav_path)
    response = HTTPResponseBody(ok=True, msg='推理成功', data={'transcript': transcript})
    return jsonify(asdict(response))


def start():
    config = initzr.load_asr_config()
    _init(config)
    app.run(host=config.host, port=config.port, debug=config.debug)
