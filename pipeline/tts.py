from urllib.parse import urljoin

from zerolan.data.abs_data import AbstractModelQuery
from zerolan.data.data.tts import TTSQuery, TTSPrediction

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
        return super().predict(query)

    @pipeline_resolve()
    def stream_predict(self, query: TTSQuery):
        return super().stream_predict(query)

    def parse_query(self, query: any) -> dict:
        assert isinstance(query, AbstractModelQuery)
        return query.model_dump()

    def parse_prediction(self, data: bytes) -> TTSPrediction:
        audio_type = check_audio_format(data)
        return TTSPrediction(wave_data=data, audio_type=audio_type)
