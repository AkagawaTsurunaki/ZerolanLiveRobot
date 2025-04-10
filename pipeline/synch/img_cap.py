from requests import Response
from zerolan.data.pipeline.img_cap import ImgCapQuery, ImgCapPrediction

from ump.abs_pipeline import AbstractImagePipeline
from ump.config import ImgCapPipelineConfig


class ImgCapPipeline(AbstractImagePipeline):

    def __init__(self, config: ImgCapPipelineConfig):
        super().__init__(config)

    def predict(self, query: ImgCapQuery) -> ImgCapPrediction | None:
        assert isinstance(query, ImgCapQuery)
        return super().predict(query)

    def stream_predict(self, query: ImgCapQuery, chunk_size: int | None = None):
        assert isinstance(query, ImgCapQuery)
        raise NotImplementedError()

    def parse_query(self, query: any) -> dict:
        return super().parse_query(query)

    def parse_prediction(self, response: Response) -> ImgCapPrediction:
        json_val = response.content
        return ImgCapPrediction.model_validate_json(json_val)
