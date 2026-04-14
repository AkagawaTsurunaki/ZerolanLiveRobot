import os

from requests import Response
from zerolan.data.pipeline.vid_cap import VidCapQuery, VidCapPrediction

from pipeline.base.base_sync import CommonModelPipeline
from pipeline.vidcap.config import VidCapPipelineConfig, VidCapModelIdEnum
from pipeline.vidcap.openai_vidcap import OpenAIVidCapPipeline


class VidCapSyncPipeline(CommonModelPipeline):

    def __init__(self, config: VidCapPipelineConfig):
        """
        此接口保留，但是可能会在将来废弃而放弃维护
        :param config:
        """
        super().__init__(config)
        # Check if using OpenAI format
        if config.model_id == VidCapModelIdEnum.OtherOpenAIFormat and config.openai_format_config is not None:
            openai_pipeline = OpenAIVidCapPipeline(config.openai_format_config)
            self.predict = openai_pipeline.predict
            self.stream_predict = openai_pipeline.stream_predict

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
