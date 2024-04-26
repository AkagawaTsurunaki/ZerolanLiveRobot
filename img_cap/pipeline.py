from dataclasses import dataclass

from common.abs_pipeline import AbstractPipeline, AbstractModelQuery, AbstractModelResponse
from config import GlobalConfig


@dataclass
class ImageCapQuery(AbstractModelQuery):
    img_path: str
    prompt: str


@dataclass
class ImageCapResponse(AbstractModelResponse):
    caption: str


class ImageCapPipeline(AbstractPipeline):
    def __init__(self, cfg: GlobalConfig):
        super().__init__()
        host, port = cfg.image_captioning.host, cfg.image_captioning.port
        self.predict_url = f'http://{host}:{port}/image-captioning/predict'

    def predict(self, query: ImageCapQuery) -> ImageCapResponse | None:
        return super().predict(query)

    @staticmethod
    def parse_response_from_json(obj: any) -> ImageCapResponse:
        caption = obj['caption']
        return ImageCapResponse(caption=caption)

    @staticmethod
    def parse_query_from_json(obj: any) -> ImageCapQuery:
        img_path = obj['img_path']
        prompt = obj['prompt']
        return ImageCapQuery(img_path=img_path, prompt=prompt)
