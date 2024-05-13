from dataclasses import asdict

from flask import Flask, request, jsonify, stream_with_context, Response
from loguru import logger

from llm.pipeline import LLMPipeline
from common.datacls import ModelNameConst as MNC, LLMQuery
from config import GLOBAL_CONFIG as G_CFG

_app = Flask(__name__)

model_name: str = G_CFG.large_language_model.models[0].model_name


def _model_predict(llm_query: LLMQuery):
    if not isinstance(llm_query, LLMQuery):
        raise ValueError('“llm_query” 必须是 LLMQuery 的实例。')
    if MNC.CHATGLM3 == model_name:
        import llm.chatglm3.app
        return llm.chatglm3.app.predict(llm_query)
    elif MNC.QWEN == model_name:
        import llm.qwen.app
        return llm.qwen.app.predict(llm_query)
    elif MNC.SHISA == model_name:
        import llm.shisa.app
        return llm.shisa.app.predict(llm_query)
    elif MNC.YI == model_name:
        import llm.yi_6b.app
        return llm.yi_6b.app.predict(llm_query)


def _model_stream_predict(llm_query: LLMQuery):
    if not isinstance(llm_query, LLMQuery):
        raise ValueError('"llm_query" must be an instance of LLMQuery.')
    if MNC.CHATGLM3 == model_name:
        import llm.chatglm3.app
        yield llm.chatglm3.app.stream_predict(llm_query)
    elif MNC.QWEN == model_name:
        import llm.qwen.app
        yield llm.qwen.app.stream_predict(llm_query)
    raise NotImplementedError('This route has not been implemented yet.')


def _to_pipeline_format() -> LLMQuery:
    logger.info('↘️ 请求接受：处理中……')
    json_val = request.get_json()
    llm_query = LLMPipeline.parse_query_from_json(json_val)
    logger.info(f'🤔 用户输入： {llm_query.text}')
    return llm_query


@_app.route('/llm/predict', methods=['GET', 'POST'])
def _handle_predict():
    """
    处理推理请求
    :return:
    """
    llm_query = _to_pipeline_format()
    llm_response = _model_predict(llm_query)
    logger.info(f'✅ 模型响应：{llm_response.response}')
    return jsonify(asdict(llm_response))


@_app.route('/llm/stream-predict', methods=['GET', 'POST'])
def _handle_stream_predict():
    """
    处理流式推理
    :return:
    """
    llm_query = _to_pipeline_format()

    def generate_output(q: LLMQuery):
        with _app.app_context():
            for llm_response in next(_model_stream_predict(q)):
                logger.info(f'✅ 模型响应：{llm_response.response}')
                yield jsonify(llm_response).data + b'\n'

    return Response(stream_with_context(generate_output(llm_query)), content_type='application/json')


def start():
    host, port, debug = G_CFG.large_language_model.host, G_CFG.large_language_model.port, G_CFG.large_language_model.debug
    _app.run(host=host, port=port, debug=debug)
