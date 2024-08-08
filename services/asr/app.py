from flask import Flask, request, jsonify
from loguru import logger

from common.config.service_config import ASRServiceConfig as config
from common.register.model_register import ASRModels
from common.utils import web_util, audio_util, file_util
from common.abs_app import AbstractApplication
from services.asr.pipeline import ASRModelQuery, ASRModelStreamQuery

if config.model_id == ASRModels.SPEECH_PARAFORMER_ASR.id:
    from services.asr.paraformer.model import SpeechParaformerModel as ASRM
else:
    raise NotImplementedError("不支持此自动语音识别模型")


class ASRApplication(AbstractApplication):
    def __init__(self):
        super().__init__()
        self._app = Flask(__name__)
        self._app.add_url_rule(rule='/asr/predict', view_func=self._handle_predict,
                               methods=["GET", "POST"])
        self._app.add_url_rule(rule='/asr/stream-predict', view_func=self._handle_stream_predict,
                               methods=["GET", "POST"])
        self._asrm = ASRM()

    def run(self):
        self._asrm.load_model()
        self._app.run(config.host, config.port, False)

    def _handle_predict(self):
        logger.info('↘️ 请求接受：处理中……')

        query: ASRModelQuery = web_util.get_obj_from_json(request, ASRModelQuery)
        audio_path = web_util.save_request_audio(request, prefix="asr")

        # 转化为单声道音频
        mono_audio_path = file_util.create_temp_file(prefix="asr", suffix=".wav", tmpdir="audio")
        audio_util.convert_to_mono(audio_path, mono_audio_path, query.sample_rate)
        query.audio_path = mono_audio_path

        prediction = self._asrm.predict(query)

        return jsonify(prediction.to_dict())  # type: ignore[attr-defined]

    def _handle_stream_predict(self):
        """

        Returns:

        """
        query: ASRModelStreamQuery = web_util.get_obj_from_json(request, ASRModelStreamQuery)
        audio_data = web_util.get_request_audio_file(request).stream.read()
        query.audio_data = audio_data

        prediction = self._asrm.stream_predict(query)
        return jsonify(prediction.to_dict())  # type: ignore[attr-defined]
