import os

from pydantic import Field
from requests import Response
from zerolan.data.pipeline.vid_cap import VidCapQuery, VidCapPrediction

from ump.abs_pipeline import CommonModelPipeline, AbstractPipelineConfig


class VidCapPipelineConfig(AbstractPipelineConfig):
    model_id: str = Field(default="iic/multi-modal_hitea_video-captioning_base_en",
                          description="The ID of the model used for video captioning.")
    predict_url: str = Field(default="http://127.0.0.1:11000/vid_cap/predict",
                             description="The URL for video captioning prediction requests.")
    stream_predict_url: str = Field(default="http://127.0.0.1:11000/vid-cap/stream-predict",
                                    description="The URL for streaming video captioning prediction requests.")


class VidCapPipeline(CommonModelPipeline):

    def __init__(self, config: VidCapPipelineConfig):
        """
        此接口保留，但是可能会在将来废弃而放弃维护
        :param config:
        """
        super().__init__(config)

    def predict(self, query: VidCapQuery) -> VidCapPrediction | None:
        assert isinstance(query, VidCapQuery)
        assert os.path.exists(query.vid_path), f"视频路径不存在：{query.vid_path}"
        return super().predict(query)

    def stream_predict(self, query: VidCapQuery, chunk_size: int | None = None):
        assert isinstance(query, VidCapQuery)
        raise NotImplementedError()

    def parse_prediction(self, response: Response) -> VidCapPrediction:
        json_val = response.content
        return VidCapPrediction.model_validate(json_val)
