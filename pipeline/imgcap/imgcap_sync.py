from requests import Response
from zerolan.data.pipeline.img_cap import ImgCapQuery, ImgCapPrediction

from pipeline.base.base_sync import AbstractImagePipeline
from pipeline.imgcap.config import ImgCapPipelineConfig, ImgCapModelIdEnum
from pipeline.imgcap.openai_imgcap import OpenAIImgCapPipeline


class ImgCapSyncPipeline(AbstractImagePipeline):

    def __init__(self, config: ImgCapPipelineConfig):
        super().__init__(config)
        # Check if using OpenAI format
        if config.model_id == ImgCapModelIdEnum.OtherOpenAIFormat and config.openai_format_config is not None:
            openai_pipeline = OpenAIImgCapPipeline(config.openai_format_config)
            self.predict = openai_pipeline.predict
            self.stream_predict = openai_pipeline.stream_predict

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
