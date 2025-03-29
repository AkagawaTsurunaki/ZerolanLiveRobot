import os
from typing import Literal, Dict, Any

from typeguard import typechecked
from zerolan.data.pipeline.img_cap import ImgCapQuery, ImgCapPrediction

from ump.asyncio.pipeline.base import BaseAsyncPipeline

ModelID = Literal['Salesforce/blip-image-captioning-large']


@typechecked
def _parse_imgcap_query(query: ImgCapQuery) -> Dict[str, Any]:
    # If the `query.img_path` path exists on the local machine,
    # then read the image as a binary file and add it to the `request.files`
    if os.path.exists(query.img_path):
        query.img_path = os.path.abspath(query.img_path).replace('\\', '/')
        img = open(query.img_path, 'rb')
        data = {'image': img,
                'json': query.model_dump_json()}
        return data
    # If the `query.img_path` path does not exist on the local machine, it must exist on the remote host
    # Note: If the remote host does not have this file neither, raise 500 error!
    else:
        return query.model_dump()


class ImgCapPipeline(BaseAsyncPipeline):
    def __init__(self, model_id: ModelID, base_url: str):
        super().__init__(base_url)
        self._model_id: ModelID = model_id
        self._predict_endpoint = "/img-cap/predict"
        self._stream_predict_endpoint = "/img-cap/stream-predict"

    @typechecked
    async def predict(self, query: ImgCapQuery) -> ImgCapPrediction:
        data = _parse_imgcap_query(query)
        async with self.session.post(self._predict_endpoint, data=data) as resp:
            return await resp.json(encoding='utf8', loads=ImgCapPrediction.model_validate_json)
