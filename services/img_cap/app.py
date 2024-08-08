from dataclasses import asdict

from flask import Flask, request, jsonify
from loguru import logger

from common.utils import web_util
from common.abs_app import AbstractApplication
from common.config.service_config import ImgCapServiceConfig as config
from common.register.model_register import ICModels
from services.img_cap.pipeline import ImgCapQuery

if config.model_id == ICModels.BLIP_IMG_CAP_LARGE.id:
    from services.img_cap.blip.model import BlipImageCaptioningLarge as ICM
else:
    raise NotImplementedError("不支持此图像字幕（Image Captioning）模型")


class ImgCapApplication(AbstractApplication):

    def __init__(self):
        super().__init__()
        self._app = Flask(__name__)
        # 兼容旧 API
        self._app.add_url_rule(rule='/image-captioning/predict', view_func=self._handle_predict,
                               methods=["GET", "POST"])
        self._app.add_url_rule(rule='/img-cap/predict', view_func=self._handle_predict,
                               methods=["GET", "POST"])
        self._model = ICM()

    def run(self):
        self._model.load_model()
        self._app.run(config.host, config.port, False)

    def _to_pipeline_format(self) -> ImgCapQuery:
        with self._app.app_context():
            logger.info('↘️ 请求接受：处理中……')

            if request.headers['Content-Type'] == 'application/json':
                # 如果是 JSON 格式，那么一定存在图像地址
                json_val = request.get_json()
                query = ImgCapQuery.from_dict(json_val)
            elif 'multipart/form-data' in request.headers['Content-Type']:
                query: ImgCapQuery = web_util.get_obj_from_json(request, ImgCapQuery)
                query.img_path = web_util.save_request_image(request, prefix="imgcap")
            else:
                raise NotImplementedError("不支持的 Content-Type 类型")

            logger.info(f'🖼️ 图片地址： {query.img_path}')
            return query

    def _handle_predict(self):
        """
        应该直接传入图片。
        直接当做图片。
        Returns:

        """
        logger.info('↘️ 请求接受：处理中……')
        query = self._to_pipeline_format()
        prediction = self._model.predict(query)
        logger.info(f'✅ 模型响应：{prediction.caption}')
        return jsonify(asdict(prediction))

    def _handle_stream_predict(self):
        raise NotImplementedError("未实现路由")
