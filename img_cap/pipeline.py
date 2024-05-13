from dataclasses import dataclass

from common import util
from common.abs_pipeline import AbstractPipeline, AbstractModelQuery, AbstractModelResponse
from config import GlobalConfig


@dataclass
class ImageCaptioningModelQuery(AbstractModelQuery):
    # Base64 编码
    img_data: str
    prompt: str


@dataclass
class ImageCaptioningModelResponse(AbstractModelResponse):
    caption: str


class ImageCapPipeline(AbstractPipeline):
    def __init__(self, cfg: GlobalConfig):
        super().__init__()
        ic_cfg = cfg.image_captioning
        host, port = ic_cfg.host, ic_cfg.port
        self.predict_url = util.urljoin(host, port, '/image-captioning/predict')

    def predict(self, query: ImageCaptioningModelQuery) -> ImageCaptioningModelResponse | None:
        return super().predict(query)

    @staticmethod
    def parse_response_from_json(obj: any) -> ImageCaptioningModelResponse:
        caption = obj['caption']
        return ImageCaptioningModelResponse(caption=caption)

    @staticmethod
    def parse_query_from_json(obj: any) -> ImageCaptioningModelQuery:
        img_data = obj['img_data']
        prompt = obj['prompt']
        return ImageCaptioningModelQuery(img_data=img_data, prompt=prompt)
