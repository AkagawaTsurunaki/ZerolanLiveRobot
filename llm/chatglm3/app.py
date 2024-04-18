from dataclasses import asdict

from flask import Flask, jsonify, stream_with_context, Response, request
from loguru import logger
from transformers import AutoTokenizer, AutoModel

from llm.pipeline import LLMPipeline
from utils.datacls import LLMResponse, Chat, LLMQuery

TOKENIZER: AutoTokenizer
MODEL: AutoModel

app = Flask(__name__)


def _predict(llm_query: LLMQuery) -> LLMResponse:
    query = llm_query.text
    history = [{'role': chat.role, 'metadata': '', 'content': chat.content} for chat in llm_query.history]
    response, history = MODEL.chat(TOKENIZER, query, history, top_p=1., temperature=1., past_key_values=None)
    history = [Chat(role=chat['role'], content=chat['content']) for chat in history]
    llm_response = LLMResponse(response=response, history=history)
    return llm_response


def _stream_predict(llm_query: LLMQuery):
    query = llm_query.text
    history = [{'role': chat.role, 'metadata': '', 'content': chat.content} for chat in llm_query.history]
    yield MODEL.stream_chat(TOKENIZER, query, history=history, top_p=1., temperature=1.,
                            past_key_values=None,
                            return_past_key_values=True)


@app.route('/chatglm3/predict', methods=['GET', 'POST'])
def handle_predict():
    json_val = request.get_json()
    llm_query = LLMPipeline.convert_query_from_json(json_val)
    llm_response = _predict(llm_query)
    return jsonify(asdict(llm_response))


@app.route('/chatglm3/stream-predict', methods=['GET', 'POST'])
def handle_stream_predict():
    json_val = request.get_json()
    print(json_val)
    llm_query = LLMPipeline.convert_query_from_json(json_val)

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


def start(model_path, quantize, host, port, debug):
    global TOKENIZER, MODEL
    TOKENIZER = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    MODEL = AutoModel.from_pretrained(model_path, trust_remote_code=True).quantize(quantize).to(
        'cuda').eval()
    logger.info(f'💭 ChatGLM3 以 {quantize}-bit 加载完毕')
    app.run(host=host, port=port, debug=debug)
