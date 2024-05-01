from dataclasses import asdict

from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer

from config import GlobalConfig
from llm.pipeline import LLMPipeline, LLMQuery, LLMResponse, Chat, Role

# Global attributes
_app = Flask(__name__)  # Flask application instance

_host: str  # Host address for the Flask application
_port: int  # Port number for the Flask application
_debug: bool  # Debug mode flag for the Flask application

_tokenizer: any  # Tokenizer for the language model
_model: any  # Language model for generating responses


def init(cfg: GlobalConfig):
    """
    Initializes the application with the given configuration.

    Args:
        cfg (GlobalConfig): Configuration object containing settings for the application.
    """
    global _model, _tokenizer, _host, _port, _debug
    mode = cfg.large_language_model.models[0].loading_mode
    model_path = cfg.large_language_model.models[0].model_path

    _host = cfg.large_language_model.host
    _port = cfg.large_language_model.port
    _debug = cfg.large_language_model.debug

    # Load model on given mode
    if mode == 'bf16':
        _model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto", trust_remote_code=True,
                                                      bf16=True).eval()
    elif mode == 'fp16':
        _model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto", trust_remote_code=True,
                                                      fp16=True).eval()
    elif mode == 'cpu':
        _model = AutoModelForCausalLM.from_pretrained(model_path, device_map="cpu", trust_remote_code=True).eval()
    else:
        _model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto", trust_remote_code=True).eval()

    # Load auto _tokenizer
    _tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)


def start():
    """
    Starts the Flask application with the configured host, port, and debug mode.
    """
    # Run application
    _app.run(host=_host, port=_port, debug=_debug)


def _predict(llm_query: LLMQuery):
    """
    Generates a response from the language model based on the given query.

    Args:
        llm_query (llm.pipeline.LLMQuery): The query containing the text and conversation history.

    Returns:
        llm.pipeline.LLMResponse: The response generated by the language model, including the response text and updated conversation history.
    """
    history_content_list: list[str] = [chat.content for chat in llm_query.history]

    sys_prompt = None
    # Concat system prompt with the first conversation content
    if llm_query.history[0].role == Role.SYSTEM:
        sys_prompt = llm_query.history[0].content
        if len(history_content_list) > 0:
            history_content_list = history_content_list[1:]
            history_content_list[0] = sys_prompt + history_content_list[0]

    assert len(history_content_list) % 2 == 0, f'Length of the history for Qwen must be even number.'

    # Convert content list as tuple
    history: list[tuple] = []

    for i in range(0, len(history_content_list), 2):
        history.append((history_content_list[i], history_content_list[i + 1]))

    response, history = _model.chat(_tokenizer, llm_query.text, history=history)

    assert isinstance(history, list)
    assert all(isinstance(item, tuple) for item in history)

    # Convert history tuples to pipeline format
    ret_history: list[Chat] = []
    for chat in history:
        q, r = chat[0], chat[1]
        assert isinstance(q, str) and isinstance(r, str)
        ret_history.append(Chat(role=Role.USER, content=q))
        ret_history.append(Chat(role=Role.ASSISTANT, content=r))

    # Extract system prompt from history
    if sys_prompt:
        ret_history[0].content = ret_history[0].content[len(sys_prompt):]
        ret_history.insert(0, Chat(role=Role.SYSTEM, content=sys_prompt))

    llm_response = LLMResponse(response=response, history=ret_history)
    return llm_response


@_app.route('/llm/predict', methods=['GET', 'POST'])
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


@_app.route('/llm/stream-predict', methods=['GET', 'POST'])
def _handle_stream_predict():
    """
    Handles streaming prediction requests. This route has not been implemented yet.

    Raises:
        NotImplementedError: Indicates that the route is not implemented.
    """
    raise NotImplementedError('This route has not been implemented yet.')
