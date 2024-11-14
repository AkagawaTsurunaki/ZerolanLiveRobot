from urllib.parse import urljoin

from zerolan.data.data.tts import TTSQuery, TTSPrediction

from common.config import TTSPipelineConfig as TTSPipelineConfig
from pipeline.abs_pipeline import AbstractPipeline


class TTSPipeline(AbstractPipeline):

    def __init__(self, config: TTSPipelineConfig):
        super().__init__(config)
        self.predict_url = urljoin(config.server_url, '/tts/predict')
        self.stream_predict_url = urljoin(config.server_url, f'/tts/stream-predict')
        self.state_url = urljoin(config.server_url, '/tts/state')
        self.check_urls()

    def predict(self, query: TTSQuery) -> TTSPrediction | None:
        return super().predict(query)

    def stream_predict(self, query: TTSQuery):
        return super().stream_predict(query)

    def parse_query(self, query: any) -> dict:
        assert hasattr(query, 'to_dict')
        return query.to_dict()

    def parse_prediction(self, data: bytes) -> TTSPrediction:
        return TTSPrediction(wave_data=data)
