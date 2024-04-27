from dataclasses import asdict

from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer, LlamaTokenizer

from common.datacls import LLMResponse, Role, Chat
from llm.pipeline import LLMPipeline

app = Flask(__name__)

_host: str
_port: int
_debug: bool

_tokenizer: LlamaTokenizer
_model: any


def init(cfg):
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
        torch_dtype='auto'
    ).eval()


def start():
    global _host, _port, _debug
    app.run(host=_host, port=_port, debug=_debug)


def _predict(llm_query):
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


@app.route('/llm/predict', methods=['GET', 'POST'])
def handle_predict():
    json_val = request.get_json()
    llm_query = LLMPipeline.parse_query_from_json(json_val)
    llm_response = _predict(llm_query)
    return jsonify(asdict(llm_response))


@app.route('/llm/stream-predict', methods=['GET', 'POST'])
def handle_stream_predict():
    raise NotImplementedError('This route has not been implemented yet.')
