import os.path
from urllib.parse import urljoin

from zerolan.data.pipeline.abs_data import AbstractModelQuery
from zerolan.data.pipeline.tts import TTSQuery, TTSPrediction

from common.config import TTSPipelineConfig as TTSPipelineConfig
from common.decorator import pipeline_resolve
from common.utils.audio_util import check_audio_format
from pipeline.abs_pipeline import AbstractPipeline


class TTSPipeline(AbstractPipeline):

    def __init__(self, config: TTSPipelineConfig):
        super().__init__(config)
        self.predict_url = urljoin(config.server_url, '/tts/predict')
        self.stream_predict_url = urljoin(config.server_url, f'/tts/stream-predict')
        self.state_url = urljoin(config.server_url, '/tts/state')
        self.check_urls()

    @pipeline_resolve()
    def predict(self, query: TTSQuery) -> TTSPrediction | None:
        if os.path.exists(query.refer_wav_path):
            query.refer_wav_path = os.path.abspath(query.refer_wav_path)
        return super().predict(query)

    @pipeline_resolve()
    def stream_predict(self, query: TTSQuery):
        return super().stream_predict(query)

    def parse_prediction(self, data: bytes) -> TTSPrediction:
        audio_type = check_audio_format(data)
        return TTSPrediction(wave_data=data, audio_type=audio_type)
