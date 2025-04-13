import os.path

from typeguard import typechecked
from zerolan.data.pipeline.vid_cap import VidCapQuery, VidCapPrediction

from pipeline.base.base_async import BaseAsyncPipeline, get_base_url
from pipeline.vidcap.config import VidCapPipelineConfig, VidCapModelIdEnum


def _parse_vid_cap_query(query: VidCapQuery):
    if os.path.exists(query.vid_path):
        query.vid_path = os.path.abspath(query.vid_path).replace("\\", "/")
    return query


class VidCapAsyncPipeline(BaseAsyncPipeline):
    def __init__(self, config: VidCapPipelineConfig):
        super().__init__(base_url=get_base_url(config.predict_url))
        self._model_id: VidCapModelIdEnum = config.model_id
        self._predict_endpoint = "/vid-cap/predict"

    @typechecked
    async def predict(self, query: VidCapQuery) -> VidCapPrediction:
        data = _parse_vid_cap_query(query)
        async with self.session.post(self._predict_endpoint, json=data.model_dump()) as resp:
            return await resp.json(encoding='utf8', loads=VidCapPrediction.model_validate_json)
