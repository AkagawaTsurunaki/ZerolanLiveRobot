from typeguard import typechecked
from zerolan.data.pipeline.vla import ShowUiPrediction, ShowUiQuery

from pipeline.base.base_async import BaseAsyncPipeline, get_base_url
from pipeline.vla.config import VLAModelIdEnum
from pipeline.vla.showui.config import ShowUIConfig


class ShowUIAsyncPipeline(BaseAsyncPipeline):
    def __init__(self, config: ShowUIConfig):
        super().__init__(base_url=get_base_url(config.predict_url))
        assert str(config.model_id) == VLAModelIdEnum.ShowUI.value, f"Model ID is wrong."
        self._model_id: VLAModelIdEnum = VLAModelIdEnum.ShowUI
        self._predict_endpoint = "/vla/showui/predict"

    @typechecked
    async def predict(self, query: ShowUiQuery) -> ShowUiPrediction:
        async with self.session.post(self._predict_endpoint, json=query.model_dump()) as resp:
            return await resp.json(encoding='utf8', loads=ShowUiPrediction.model_validate_json)
