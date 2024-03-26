from flask import Flask, jsonify, stream_with_context, Response, request
from loguru import logger
from transformers import AutoTokenizer, AutoModel

import utils.util
from utils.datacls import LLMQuery
from utils.util import url_join

# 该服务是否已被初始化?
g_is_service_inited = False

# 该服务是否正在运行?
g_is_service_running = False

DEBUG: bool = False
HOST: str = '127.0.0.1'
PORT: int = 8085
TOKENIZER: AutoTokenizer
MODEL: AutoModel
MODEL_PROMPT = None
SERVICE_URL = 'http://127.0.0.1:8085'

app = Flask(__name__)


def predict(query: str, history: list = None, top_p: float = 1., temperature: float = 1.,
            return_past_key_values: bool = True) -> (str, list):
    ret_response = ''
    ret_history = None
    past_key_values = None

    for response, history, past_key_values in MODEL.stream_chat(TOKENIZER,
                                                                query,
                                                                history=history if history else [],
                                                                top_p=top_p,
                                                                temperature=temperature,
                                                                past_key_values=past_key_values,
                                                                return_past_key_values=return_past_key_values):
        ret_response = response
        ret_history = history

    return ret_response, ret_history


def stream_predict(query: str, history: list = None, top_p: float = 1., temperature: float = 1.,
                   return_past_key_values: bool = True):
    past_key_values = None

    yield MODEL.stream_chat(TOKENIZER,
                            query,
                            history=history if history else [],
                            top_p=top_p,
                            temperature=temperature,
                            past_key_values=past_key_values,
                            return_past_key_values=return_past_key_values)


@app.route('/predict', methods=['POST'])
def handle_output():
    json_val = request.get_json()
    llm_query = LLMQuery(**json_val)
    response, history = predict(query=llm_query.query, history=llm_query.history, temperature=llm_query.temperature,
                                top_p=llm_query.top_p,
                                return_past_key_values=True)
    print(response)
    return jsonify({
        "response": response,
        "history": history
    })


@app.route('/streampredict', methods=['POST'])
def handle_stream_output():
    json_val = request.get_json()
    llm_query = LLMQuery(**json_val)

    def generate_output(llm_query: LLMQuery):
        with app.app_context():
            for response, history, past_key_values in next(
                    stream_predict(
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


def init(debug, host, port, tokenizer_path, model_path, quantize):
    global TOKENIZER, MODEL, g_is_service_inited, MODEL_PROMPT, DEBUG, SERVICE_URL, HOST, PORT
    DEBUG = debug
    HOST = host
    PORT = port
    SERVICE_URL = url_join(host, port)
    TOKENIZER = AutoTokenizer.from_pretrained(tokenizer_path, trust_remote_code=True)
    MODEL = AutoModel.from_pretrained(model_path, trust_remote_code=True).quantize(quantize).to('cuda').eval()
    g_is_service_inited = True
    logger.info(f'💭 ChatGLM3 以 {quantize}-bit 加载完毕, API 服务开启于 {SERVICE_URL}')
    return g_is_service_inited


def start():
    global g_is_service_running
    g_is_service_running = True
    app.run(host=HOST, port=PORT, debug=DEBUG)


def stop():
    utils.util.shutdown_server()
