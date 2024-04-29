from dataclasses import dataclass

from common.abs_pipeline import AbstractPipeline, AbstractModelQuery, AbstractModelResponse
from config import ImageCaptioningConfig


@dataclass
class ImageCaptioningModelQuery(AbstractModelQuery):
    img_path: str
    prompt: str


@dataclass
class ImageCaptioningModelResponse(AbstractModelResponse):
    caption: str


class ImageCapPipeline(AbstractPipeline):
    def __init__(self, cfg: ImageCaptioningConfig):
        super().__init__()
        host, port = cfg.host, cfg.port
        self.predict_url = f'http://{host}:{port}/image-captioning/predict'

    def predict(self, query: ImageCaptioningModelQuery) -> ImageCaptioningModelResponse | None:
        return super().predict(query)

    @staticmethod
    def parse_response_from_json(obj: any) -> ImageCaptioningModelResponse:
        caption = obj['caption']
        return ImageCaptioningModelResponse(caption=caption)

    @staticmethod
    def parse_query_from_json(obj: any) -> ImageCaptioningModelQuery:
        img_path = obj['img_path']
        prompt = obj['prompt']
        return ImageCaptioningModelQuery(img_path=img_path, prompt=prompt)
