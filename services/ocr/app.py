import os.path
from dataclasses import asdict

from flask import Flask, request, jsonify
from loguru import logger

from common.utils import web_util
from common.register.model_register import OCRModels
from common.abs_app import AbstractApplication
from common.config.service_config import ServiceConfig
from services.ocr.pipeline import OCRQuery

config = ServiceConfig.ocr_config

if config.model_id == OCRModels.PADDLE_OCR.id:
    from services.ocr.paddle.model import PaddleOCRModel as OCRModel
else:
    raise NotImplementedError(f"不支持的光学字符识别模型：{config.model_id}")


class OCRApplication(AbstractApplication):
    def __init__(self):
        super().__init__()
        self._app = Flask(__name__)
        self._app.add_url_rule(rule='/ocr/predict', view_func=self._handle_predict,
                               methods=["GET", "POST"])
        self._model = OCRModel()

    def run(self):
        self._model.load_model()
        self._app.run(config.host, config.port, False)

    def _to_pipeline_format(self) -> OCRQuery:
        with self._app.app_context():
            logger.info('↘️ 请求接受：处理中……')

            if request.headers['Content-Type'] == 'application/json':
                # 如果是 JSON 格式，那么一定存在图像地址
                json_val = request.get_json()
                query = OCRQuery.from_dict(json_val)
            elif 'multipart/form-data' in request.headers['Content-Type']:
                # 如果是 multipart/form-data 格式，那么尝试获取图像文件
                img_path = web_util.save_request_image(request, prefix="ocr")
                query = OCRQuery(img_path)
            else:
                raise NotImplementedError("不支持的 Content-Type 类型")

            logger.info(f'🖼️ 图片地址： {query.img_path}')
            return query

    def _handle_predict(self):
        query = self._to_pipeline_format()
        assert os.path.exists(query.img_path), f"图片文件不存在：{query.img_path}"
        prediction = self._model.predict(query)
        logger.info(f"推理结果：{prediction.unfold_as_str()}")
        return jsonify(asdict(prediction))

    def _handle_stream_predict(self):
        raise NotImplementedError()
