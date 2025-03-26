from pydantic import Field
from zerolan.data.pipeline.vla import ShowUiQuery, ShowUiPrediction

from ump.abs_pipeline import AbstractImagePipeline, AbstractPipelineConfig


class ShowUIConfig(AbstractPipelineConfig):
    model_id: str = Field(default="showlab/ShowUI-2B", description="The ID of the model used for the UI.")
    predict_url: str = Field(default="http://127.0.0.1:11000/vla/showui/predict",
                             description="The URL for UI prediction requests.")
    stream_predict_url: str = Field(default="http://127.0.0.1:11000/vla/showui/stream-predict",
                                    description="The URL for streaming UI prediction requests.")


class ShowUIPipeline(AbstractImagePipeline):

    def __init__(self, config: ShowUIConfig):
        super().__init__(config)

    def predict(self, query: ShowUiQuery) -> ShowUiPrediction | None:
        return super().predict(query)

    def stream_predict(self, query: ShowUiQuery, chunk_size: int | None = None):
        raise NotImplementedError()

    def parse_query(self, query: any) -> dict:
        return super().parse_query(query=query)

    def parse_prediction(self, json_val: any) -> ShowUiPrediction:
        return ShowUiPrediction.model_validate_json(json_val)
