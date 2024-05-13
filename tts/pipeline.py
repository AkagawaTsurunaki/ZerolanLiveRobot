from dataclasses import asdict
from http import HTTPStatus

import requests

from common import util
from common.abs_pipeline import AbstractPipeline
from common.datacls import ModelNameConst as SNC, TTSQuery, TTSResponse
from config import GlobalConfig


class TTSPipeline(AbstractPipeline):
    def __init__(self, cfg: GlobalConfig):
        super().__init__()
        host, port = cfg.text_to_speech.host, cfg.text_to_speech.port

        self.predict_url = util.urljoin(host, port, '/tts/predict')
        self.model_name = cfg.text_to_speech.models[0].model_name

    def predict(self, query: TTSQuery) -> TTSResponse | None:
        if SNC.GPT_SOVITS == self.model_name:
            return self._predict(query)
        else:
            raise NotImplementedError("尚未实现")

    def _predict(self, tts_query: TTSQuery) -> TTSResponse | None:
        query = asdict(tts_query)
        response = requests.post(self.predict_url, json=query)
        if response.status_code == HTTPStatus.OK:
            return TTSResponse(wave_data=response.content)
        return None
