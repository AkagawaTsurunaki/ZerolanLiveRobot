from urllib.parse import urljoin

from abs_pipeline import AbstractPipeline
from const import get_zerolan_live_robot_core_url
from zerolan.data.data.tts import TTSQuery, TTSPrediction


class TTSPipeline(AbstractPipeline):

    def __init__(self):
        super().__init__()
        self.predict_url = urljoin(get_zerolan_live_robot_core_url(), '/tts/predict')
        self.stream_predict_url = urljoin(get_zerolan_live_robot_core_url(), f'/tts/stream-predict')

    def predict(self, query: TTSQuery) -> TTSPrediction | None:
        return super().predict(query)

    def stream_predict(self, query: TTSQuery):
        return super().stream_predict(query)

    def parse_query(self, query: any) -> dict:
        assert hasattr(query, 'to_dict')
        return query.to_dict()

    def parse_prediction(self, data: bytes) -> TTSPrediction:
        return TTSPrediction(wave_data=data)
