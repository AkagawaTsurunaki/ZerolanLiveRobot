from zerolan.data.pipeline.vla import ShowUiQuery, ShowUiPrediction

from pipeline.base.base_sync import AbstractImagePipeline
from pipeline.vla.showui.config import ShowUIConfig


class ShowUISyncPipeline(AbstractImagePipeline):

    def __init__(self, config: ShowUIConfig):
        super().__init__(config)

    def predict(self, query: ShowUiQuery) -> ShowUiPrediction | None:
        assert isinstance(query, ShowUiQuery)
        return super().predict(query)

    def stream_predict(self, query: ShowUiQuery, chunk_size: int | None = None):
        assert isinstance(query, ShowUiQuery)
        raise NotImplementedError()

    def parse_query(self, query: any) -> dict:
        return super().parse_query(query=query)

    def parse_prediction(self, json_val: any) -> ShowUiPrediction:
        return ShowUiPrediction.model_validate_json(json_val)
