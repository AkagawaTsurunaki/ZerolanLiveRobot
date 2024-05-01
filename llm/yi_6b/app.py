from dataclasses import asdict

from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer, LlamaTokenizer

from llm.pipeline import LLMPipeline, LLMResponse, Role, Chat

# Global attributes
_app = Flask(__name__)  # Flask application instance

_host: str  # Host address for the Flask application
_port: int  # Port number for the Flask application
_debug: bool  # Debug mode flag for the Flask application

_tokenizer: LlamaTokenizer  # Tokenizer for the language model
_model: any  # Language model for generating responses


def init(cfg):
    """
    Initializes the application with the given configuration.

    Args:
        cfg: Configuration object containing settings for the application.
    """
    global _host, _port, _debug, _model, _tokenizer
    _host = cfg.large_language_model.host
    _port = cfg.large_language_model.port
    _debug = cfg.large_language_model.debug

    model_path = cfg.large_language_model.models[0].model_path
    mode = cfg.large_language_model.models[0].loading_mode
    _tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=False)
    _model = AutoModelForCausalLM.from_pretrained(
        model_path,
        device_map=mode,
    ).eval()


def start():
    """
    Starts the Flask application with the configured host, port, and debug mode.
    """
    global _host, _port, _debug
    _app.run(host=_host, port=_port, debug=_debug)


def _predict(llm_query):
    """
    Generates a response from the language model based on the given query.

    Args:
        llm_query: The query containing the text and conversation history.

    Returns:
        llm.pipeline.LLMResponse: The response generated by the language model, including the response text and updated conversation history.
    """
    messages = [{"role": chat.role, "content": chat.content} for chat in llm_query.history]
    messages.append({"role": Role.USER, "content": llm_query.text})

    input_ids = _tokenizer.apply_chat_template(conversation=messages, tokenize=True,
                                               add_generation_prompt=True,
                                               return_tensors='pt')
    output_ids = _model.generate(input_ids.to('cuda'))
    response = _tokenizer.decode(output_ids[0][input_ids.shape[1]:], skip_special_tokens=True)
    messages.append({"role": Role.ASSISTANT, "content": response})
    history = [Chat(role=chat['role'], content=chat['content']) for chat in messages]
    return LLMResponse(response, history)


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
