import os.path
from typing import Literal

from typeguard import typechecked
from zerolan.data.pipeline.vid_cap import VidCapQuery, VidCapPrediction

from ump.asyncio.pipeline.base import BaseAsyncPipeline

ModelID = Literal['multi-modal_hitea_video-captioning_base_en']


def _parse_vid_cap_query(query: VidCapQuery):
    if os.path.exists(query.vid_path):
        query.vid_path = os.path.abspath(query.vid_path).replace("\\", "/")
    return query


class VidCapPipeline(BaseAsyncPipeline):
    def __init__(self, model_id: ModelID, base_url: str):
        super().__init__(base_url)
        self._model_id: ModelID = model_id
        self._predict_endpoint = "/vid-cap/predict"

    @typechecked
    async def predict(self, query: VidCapQuery) -> VidCapPrediction:
        data = _parse_vid_cap_query(query)
        async with self.session.post(self._predict_endpoint, json=data.model_dump()) as resp:
            return await resp.json(encoding='utf8', loads=VidCapPrediction.model_validate_json)
