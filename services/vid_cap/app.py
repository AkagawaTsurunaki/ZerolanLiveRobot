import os.path
from dataclasses import asdict

from flask import Flask, request, jsonify
from loguru import logger

from common.register.model_register import VidCapModels
from common.utils import file_util
from common.abs_app import AbstractApplication
from common.config.service_config import ServiceConfig
from services.vid_cap.pipeline import VidCapQuery

config = ServiceConfig.vidcap_config

if config.model_id == VidCapModels.HITEA_BASE.id:
    from services.vid_cap.hitea.model import HiteaBaseModel as VidCapModel
else:
    raise NotImplementedError(f"不支持的视频字幕模型：{config.model_id}")


class VidCapApplication(AbstractApplication):

    def __init__(self):
        super().__init__()
        self._app = Flask(__name__)
        self._app.add_url_rule(rule='/vid-cap/predict', view_func=self._handle_predict,
                               methods=["GET", "POST"])
        self._model = VidCapModel()

    def run(self):
        self._model.load_model()
        self._app.run(config.host, config.port, False)

    def _to_pipeline_format(self) -> VidCapQuery:
        with self._app.app_context():
            logger.info('↘️ 请求接受：处理中……')

            if request.headers['Content-Type'] == 'application/json':
                # 如果是 JSON 格式，那么一定存在视频地址
                json_val = request.get_json()
                query = VidCapQuery.from_dict(json_val)
            elif 'multipart/form-data' in request.headers['Content-Type']:
                # 如果是 multipart/form-data 格式，那么尝试获取视频文件
                video_file = request.files.get('video', None)
                if video_file is None:
                    raise ValueError('请求中无视频数据')
                file_type = video_file.filename.split('.')[-1]
                # file_type = video_file.mimetype.split("/")[-1]
                file_type = 'mp4'
                assert file_type in ["mp4", "avi"], "不支持的视频类型"
                temp_file_path = file_util.create_temp_file(prefix="vid-cap", suffix=f".{file_type}", tmpdir="video")
                video_file.save(temp_file_path)

                logger.debug(f"临时文件创建于：{temp_file_path}")

                query = VidCapQuery(vid_path=temp_file_path)
            else:
                raise NotImplementedError("不支持的 Content-Type 类型")

            logger.info(f'📽️ 视频地址： {query.vid_path}')
            return query

    def _handle_predict(self):
        query = self._to_pipeline_format()
        assert os.path.exists(query.vid_path), ""
        prediction = self._model.predict(query)
        logger.info(f'✅ 模型响应：{prediction.caption}')
        return jsonify(asdict(prediction))

    def _handle_stream_predict(self):
        raise NotImplementedError()
