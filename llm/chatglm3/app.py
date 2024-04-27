from dataclasses import asdict

from flask import Flask, jsonify, stream_with_context, Response, request
from loguru import logger
from transformers import AutoTokenizer, AutoModel

from common.datacls import LLMResponse, Chat, LLMQuery
from config import GlobalConfig
from llm.pipeline import LLMPipeline

_tokenizer: AutoTokenizer
_model: AutoModel
app = Flask(__name__)
_host: str
_port: int
_debug: bool


def _predict(llm_query: LLMQuery) -> LLMResponse:
    query = llm_query.text
    history = [{'role': chat.role, 'metadata': '', 'content': chat.content} for chat in llm_query.history]
    response, history = _model.chat(_tokenizer, query, history, top_p=1., temperature=1., past_key_values=None)
    logger.info(response)
    history = [Chat(role=chat['role'], content=chat['content']) for chat in history]
    llm_response = LLMResponse(response=response, history=history)
    return llm_response


def _stream_predict(llm_query: LLMQuery):
    query = llm_query.text
    history = [{'role': chat.role, 'metadata': '', 'content': chat.content} for chat in llm_query.history]
    yield _model.stream_chat(_tokenizer, query, history=history, top_p=1., temperature=1.,
                             past_key_values=None,
                             return_past_key_values=True)


@app.route(f'/llm/predict', methods=['GET', 'POST'])
def handle_predict():
    json_val = request.get_json()
    llm_query = LLMPipeline.parse_query_from_json(json_val)
    llm_response = _predict(llm_query)
    return jsonify(asdict(llm_response))


@app.route(f'/llm/stream-predict', methods=['GET', 'POST'])
def handle_stream_predict():
    json_val = request.get_json()
    print(json_val)
    llm_query = LLMPipeline.parse_query_from_json(json_val)

    def generate_output(q: LLMQuery):
        with app.app_context():
            for response, history, past_key_values in next(_stream_predict(q)):
                history = [Chat(role=chat['role'], content=chat['content']) for chat in history]
                llm_response = LLMResponse(
                    response=response,
                    history=history
                )
                yield jsonify(llm_response).data + b'\n'

    return Response(stream_with_context(generate_output(llm_query)), content_type='application/json')


def init(cfg: GlobalConfig):
    global _host, _port, _debug, _model, _tokenizer
    _host = cfg.large_language_model.host
    _port = cfg.large_language_model.port
    _debug = cfg.large_language_model.debug
    model_path = cfg.large_language_model.models[0].model_path
    quantize = cfg.large_language_model.models[0].quantize
    _tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    if quantize:
        _model = AutoModel.from_pretrained(model_path, trust_remote_code=True).quantize(quantize).to(
            'cuda').eval()
    else:
        _model = AutoModel.from_pretrained(model_path, trust_remote_code=True).to('cuda').eval()
    logger.info(f'💭 ChatGLM3 model loaded.')


def start():
    app.run(host=_host, port=_port, debug=_debug)
