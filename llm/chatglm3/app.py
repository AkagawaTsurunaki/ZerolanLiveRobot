from dataclasses import asdict

from flask import Flask, jsonify, stream_with_context, Response, request
from loguru import logger
from transformers import AutoTokenizer, AutoModel

import initzr
from config.global_config import Chatglm3ServiceConfig

from llm.pipeline import LLMPipeline
from utils.datacls import LLMQuery, NewLLMResponse, Chat, NewLLMQuery

TOKENIZER: AutoTokenizer
MODEL: AutoModel

app = Flask(__name__)


def _predict(llm_query: NewLLMQuery) -> (str, list):
    query = llm_query.text
    history = [{'role': chat.role, 'metadata': '', 'content': chat.content} for chat in llm_query.history]
    response, history = MODEL.chat(TOKENIZER, query, history, top_p=1., temperature=1., past_key_values=None,
                                   return_past_key_values=True)
    history = [Chat(role=chat['role'], content=chat['content']) for chat in history]
    llm_response = NewLLMResponse(response=response, history=history)
    return llm_response
    # ret_response = ''
    # ret_history = None
    # past_key_values = None

    # for response, history, past_key_values in MODEL.stream_chat(TOKENIZER,
    #                                                             query,
    #                                                             history=history if history else [],
    #                                                             top_p=1.,
    #                                                             temperature=1.,
    #                                                             past_key_values=past_key_values,
    #                                                             return_past_key_values=True):
    #     ret_response = response
    #     ret_history = history


def _stream_predict(query: str, history: list = None, top_p: float = 1., temperature: float = 1.,
                    return_past_key_values: bool = True):
    past_key_values = None

    yield MODEL.stream_chat(TOKENIZER,
                            query,
                            history=history if history else [],
                            top_p=top_p,
                            temperature=temperature,
                            past_key_values=past_key_values,
                            return_past_key_values=return_past_key_values)


@app.route('/chatglm3/predict', methods=['GET', 'POST'])
def handle_output():
    json_val = request.get_json()
    llm_query = LLMPipeline.convert_query_from_json(json_val)
    llm_response = _predict(llm_query)
    return jsonify(asdict(llm_response))


@app.route('/chatglm3/streampredict', methods=['GET'])
def handle_stream_output():
    json_val = request.get_json()
    llm_query = LLMQuery(**json_val)

    def generate_output(llm_query: LLMQuery):
        with app.app_context():
            for response, history, past_key_values in next(
                    _stream_predict(
                        query=llm_query.query,
                        history=llm_query.history,
                        top_p=llm_query.top_p,
                        temperature=llm_query.temperature,
                        return_past_key_values=True
                    )
            ):
                print(response)
                yield jsonify({
                    "response": response,
                    "history": history
                }).data + b'\n'

    return Response(stream_with_context(generate_output(llm_query)), content_type='application/json')


def _init(config: Chatglm3ServiceConfig):
    global TOKENIZER, MODEL
    TOKENIZER = AutoTokenizer.from_pretrained(config.tokenizer_path, trust_remote_code=True)
    MODEL = AutoModel.from_pretrained(config.model_path, trust_remote_code=True).quantize(config.quantize).to(
        'cuda').eval()
    logger.info(f'💭 ChatGLM3 以 {config.quantize}-bit 加载完毕')


def start():
    config = initzr.load_chatglm3_service_config()
    _init(config)
    app.run(host=config.host, port=config.port, debug=config.debug)
