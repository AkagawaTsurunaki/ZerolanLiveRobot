from pydantic import Field
from requests import Response
from zerolan.data.pipeline.abs_data import AbstractModelQuery
from zerolan.data.pipeline.img_cap import ImgCapQuery, ImgCapPrediction

from ump.abs_pipeline import AbstractImagePipeline, AbstractPipelineConfig


class ImgCapPipelineConfig(AbstractPipelineConfig):
    model_id: str = Field(default="Salesforce/blip-image-captioning-large",
                          description="The ID of the model used for image captioning.")
    predict_url: str = Field(default="http://127.0.0.1:11000/llm/predict",
                             description="The URL for image captioning prediction requests.")
    stream_predict_url: str = Field(default="http://127.0.0.1:11000/llm/stream-predict",
                                    description="The URL for streaming image captioning prediction requests.")


class ImgCapPipeline(AbstractImagePipeline):

    def __init__(self, config: ImgCapPipelineConfig):
        super().__init__(config)

    def predict(self, query: ImgCapQuery) -> ImgCapPrediction | None:
        return super().predict(query)

    def stream_predict(self, query: AbstractModelQuery, chunk_size: int | None = None):
        raise NotImplementedError()

    def parse_query(self, query: any) -> dict:
        return super().parse_query(query)

    def parse_prediction(self, response: Response) -> ImgCapPrediction:
        json_val = response.content
        return ImgCapPrediction.model_validate_json(json_val)
