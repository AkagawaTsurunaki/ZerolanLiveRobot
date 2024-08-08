from dataclasses import asdict

from flask import Flask, jsonify, request, Response, stream_with_context
from loguru import logger

from common.abs_app import AbstractApplication
from common.config.service_config import ServiceConfig
from common.register.model_register import LLMModels
from services.llm.pipeline import LLMQuery

config = ServiceConfig.llm_config

# 根据配置文件选择不同的模型
if config.model_id == LLMModels.CHATGLM3_6B.id:
    from services.llm.chatglm3.model import ChatGLM3_6B as LLM
elif config.model_id == LLMModels.QWEN_7B_CHAT.id:
    from services.llm.qwen.model import Qwen7BChat as LLM
elif config.model_id == LLMModels.SHISA_7B_V1.id:
    from services.llm.shisa.model import Shisa7B_V1 as LLM
elif config.model_id == LLMModels.YI_6B_CHAT.id:
    from services.llm.yi.model import Yi6B_Chat as LLM
else:
    raise NotImplementedError("不支持此大语言模型")


class LLMApplication(AbstractApplication):

    def __init__(self):
        super().__init__()
        self._app = Flask(__name__)
        self._app.add_url_rule(rule='/llm/predict', view_func=self._handle_predict,
                               methods=["GET", "POST"])
        self._app.add_url_rule(rule='/llm/stream-predict', view_func=self._handle_stream_predict,
                               methods=["GET", "POST"])
        self._llm = LLM()

    def run(self):
        self._llm.load_model()
        self._app.run(config.host, config.port, False)

    def _to_pipeline_format(self) -> LLMQuery:
        with self._app.app_context():
            logger.info('↘️ 请求接受：处理中……')
            json_val = request.get_json()
            llm_query = LLMQuery.from_dict(json_val)
            logger.info(f'🤔 用户输入： {llm_query.text}')
            return llm_query

    def _handle_predict(self):
        """
        处理推理
        Returns:

        """
        llm_query = self._to_pipeline_format()
        p = self._llm.predict(llm_query)
        logger.info(f'✅ 模型响应：{p.response}')
        return jsonify(asdict(p))

    def _handle_stream_predict(self):
        """
        处理流式推理
        :return:
        """
        llm_query = self._to_pipeline_format()

        def generate_output(q: LLMQuery):
            with self._app.app_context():
                for p in self._llm.stream_predict(q):
                    logger.info(f'✅ 模型响应（流式）：{p.response}')
                    yield jsonify(p.to_dict()).data + b'\n'

        return Response(stream_with_context(generate_output(llm_query)), content_type='application/json')
