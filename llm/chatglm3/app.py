from dataclasses import asdict

from flask import Flask, jsonify, stream_with_context, Response, request
from loguru import logger
from transformers import AutoTokenizer, AutoModel

from config import GLOBAL_CONFIG as G_CFG
from llm.pipeline import LLMPipeline
from common.datacls import ModelNameConst as MNC, Chat, LLMQuery, LLMResponse

# Global attributes
_app = Flask(__name__)  # Flask application instance

_host: str  # Host address for the Flask application
_port: int  # Port number for the Flask application
_debug: bool  # Debug mode flag for the Flask application

_tokenizer: any  # Tokenizer for the language model
_model: any  # Language model for generating responses


def init():
    logger.info(f'💭 Application {MNC.CHATGLM3} is initializing...')
    global _host, _port, _debug, _model, _tokenizer

    llm_cfg = G_CFG.large_language_model
    _host, _port, _debug = llm_cfg.host, llm_cfg.port, llm_cfg.debug
    model_path, quantize = llm_cfg.models[0].model_path, llm_cfg.models[0].quantize

    logger.info(f'💭 Model {MNC.CHATGLM3} is loading...')
    _tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    if quantize:
        _model = AutoModel.from_pretrained(model_path, trust_remote_code=True).quantize(quantize).to(
            'cuda').eval()
    else:
        _model = AutoModel.from_pretrained(model_path, trust_remote_code=True).to('cuda').eval()
    assert _tokenizer and _model, f'❌️ Model {MNC.CHATGLM3} failed to load.'
    logger.info(f'💭 Model {MNC.CHATGLM3} loaded successfully..')

    logger.info(f'💭 Application {MNC.CHATGLM3} initialized successfully.')


def start():
    """
    Starts the Flask application with the configured host, port, and debug mode.
    """
    logger.info(f'💭 Application {MNC.CHATGLM3} is starting...')
    _app.run(host=_host, port=_port, debug=_debug)
    logger.info(f'💭 Application {MNC.CHATGLM3} is stopped.')


def _predict(llm_query: LLMQuery) -> LLMResponse:
    """
    Generates a response from the language model based on the given query.

    Args:
        llm_query (common.datacls.LLMQuery): The query containing the text and conversation history.

    Returns:
        common.datacls.LLMResponse: The response generated by the language model, including the response text and updated conversation history.
    """
    query = llm_query.text
    history = [{'role': chat.role, 'metadata': '', 'content': chat.content} for chat in llm_query.history]
    response, history = _model.chat(_tokenizer, query, history, top_p=1., temperature=1., past_key_values=None)
    logger.info(response)
    history = [Chat(role=chat['role'], content=chat['content']) for chat in history]
    llm_response = LLMResponse(response=response, history=history)
    return llm_response


def _stream_predict(llm_query: LLMQuery):
    """
    Streams responses from the language model based on the given query.

    Args:
        llm_query (common.datacls.LLMQuery): The query containing the text and conversation history.

    Yields:
        dict: The response generated by the language model, including (response, history, past_key_values).
    """
    query = llm_query.text
    history = [{'role': chat.role, 'metadata': '', 'content': chat.content} for chat in llm_query.history]
    yield _model.stream_chat(_tokenizer, query, history=history, top_p=1., temperature=1.,
                             past_key_values=None,
                             return_past_key_values=True)


@_app.route(f'/llm/predict', methods=['GET', 'POST'])
def _handle_predict():
    """
    Handles prediction requests by generating a response from the language model based on the received query.

    Returns:
        Response: A JSON response containing the generated response and conversation history.
    """
    json_val = request.get_json()
    llm_query = LLMPipeline.parse_query_from_json(json_val)
    llm_response = _predict(llm_query)
    return jsonify(asdict(llm_response))


@_app.route(f'/llm/stream-predict', methods=['GET', 'POST'])
def _handle_stream_predict():
    """
    Handles streaming prediction requests by streaming responses from the language model based on the received query.

    Returns:
        Response: A streaming JSON response containing the generated responses and conversation history.
    """
    json_val = request.get_json()
    print(json_val)
    llm_query = LLMPipeline.parse_query_from_json(json_val)

    def generate_output(q: LLMQuery):
        with _app.app_context():
            for response, history, past_key_values in next(_stream_predict(q)):
                history = [Chat(role=chat['role'], content=chat['content']) for chat in history]
                llm_response = LLMResponse(
                    response=response,
                    history=history
                )
                yield jsonify(llm_response).data + b'\n'

    return Response(stream_with_context(generate_output(llm_query)), content_type='application/json')
