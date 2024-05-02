from dataclasses import asdict, dataclass
from http import HTTPStatus

import requests

from common.abs_pipeline import AbstractPipeline, AbstractModelQuery, AbstractModelResponse
from config import GlobalConfig
from common.datacls import ServiceNameConst as SNC
from common import util

@dataclass
class TTSQuery(AbstractModelQuery):
    text: str
    text_language: str
    refer_wav_path: str
    prompt_text: str
    prompt_language: str


@dataclass
class TTSResponse(AbstractModelResponse):
    wave_data: bytes


class TTSPipeline(AbstractPipeline):
    def __init__(self, cfg: GlobalConfig):
        super().__init__()
        host, port = cfg.text_to_speech.host, cfg.text_to_speech.port

        self.predict_url = util.urljoin(host, port, '/tts/predict')
        self.predict_url_4_gpt_sovits = util.urljoin(host, port)
        self.model_name = cfg.text_to_speech.models[0].model_name

    def predict(self, query: TTSQuery) -> TTSResponse | None:
        if SNC.GPT_SOVITS == self.model_name:
            return self._gpt_sovits_predict(query)
        else:
            return super().predict(query)

    def _gpt_sovits_predict(self, tts_query: TTSQuery) -> TTSResponse | None:
        query = asdict(tts_query)
        response = requests.post(self.predict_url_4_gpt_sovits, json=query)
        if response.status_code == HTTPStatus.OK:
            return TTSResponse(wave_data=response.content)
        return None
