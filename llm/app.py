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
        raise ValueError('"llm_query" must be an instance of LLMQuery.')
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
    raise NotImplementedError('This route has not been implemented yet.')


@_app.route('/llm/predict', methods=['GET', 'POST'])
def _handle_predict():
    """
    Handles prediction requests by generating a response from the language model based on the received query.

    Returns:
        Response: A JSON response containing the generated response and conversation history.
    """
    logger.info('↘️ Request received: Processing...')
    json_val = request.get_json()
    llm_query = LLMPipeline.parse_query_from_json(json_val)
    llm_response = _model_predict(llm_query)
    logger.info(f'✅ Response: {llm_response.response}')
    return jsonify(asdict(llm_response))


@_app.route('/llm/stream-predict', methods=['GET', 'POST'])
def _handle_stream_predict():
    """
    Handles streaming prediction requests by streaming responses from the language model based on the received query.

    Warning: Some models may not support this method.
    :return: A streaming JSON response containing the generated responses and conversation history.

    """
    json_val = request.get_json()
    print(json_val)
    llm_query = LLMPipeline.parse_query_from_json(json_val)

    def generate_output(q: LLMQuery):
        with _app.app_context():
            for llm_response in next(_model_stream_predict(q)):
                yield jsonify(llm_response).data + b'\n'

    return Response(stream_with_context(generate_output(llm_query)), content_type='application/json')


def start():
    host, port, debug = G_CFG.large_language_model.host, G_CFG.large_language_model.port, G_CFG.large_language_model.debug
    _app.run(host=host, port=port, debug=debug)
