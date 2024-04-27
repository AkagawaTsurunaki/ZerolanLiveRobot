from dataclasses import asdict

from flask import Flask, jsonify, stream_with_context, Response, request
from loguru import logger
from transformers import AutoTokenizer, AutoModel

from common.abs_app import AbstractApp
from config import GlobalConfig
from llm.pipeline import LLMPipeline
from common.datacls import LLMResponse, Chat, LLMQuery

app = Flask(__name__)


class ChatGLM3App(AbstractApp):

    def __init__(self, cfg: GlobalConfig):
        super().__init__()
        chatglm_cfg = cfg.large_language_model.models[0]
        self._model_path = chatglm_cfg.model_path
        self._model_name = chatglm_cfg.model_name
        self._quantize = chatglm_cfg.quantize
        self.host = cfg.large_language_model.host
        self.host.port = cfg.large_language_model.port
        self.debug = cfg.large_language_model.debug

        self._tokenizer: AutoTokenizer = AutoTokenizer.from_pretrained(self._model_path, trust_remote_code=True)

        if self._quantize:
            self._model: AutoModel = AutoModel.from_pretrained(self._model_path, trust_remote_code=True) \
                .quantize(self._quantize) \
                .to('cuda').eval()
        else:
            self._model: AutoModel = AutoModel.from_pretrained(self._model_path, trust_remote_code=True) \
                .to('cuda').eval()
        logger.info(f'ChatGLM3 model loaded.')

    def start(self):
        app.run(host=self.host, port=self.port, debug=self.debug)

    def _predict(self, llm_query: LLMQuery) -> LLMResponse:
        query = llm_query.text
        history = [{'role': chat.role, 'metadata': '', 'content': chat.content} for chat in llm_query.history]
        response, history = self._model.chat(self._tokenizer, query, history, top_p=1., temperature=1.,
                                             past_key_values=None)
        logger.info(response)
        history = [Chat(role=chat['role'], content=chat['content']) for chat in history]
        llm_response = LLMResponse(response=response, history=history)
        return llm_response

    def _stream_predict(self, llm_query: LLMQuery):
        query = llm_query.text
        history = [{'role': chat.role, 'metadata': '', 'content': chat.content} for chat in llm_query.history]
        yield self._model.stream_chat(self._tokenizer, query, history=history, top_p=1., temperature=1.,
                                      past_key_values=None,
                                      return_past_key_values=True)

    @app.route(f'/llm/predict', methods=['GET', 'POST'])
    def handle_predict(self):
        json_val = request.get_json()
        llm_query = LLMPipeline.parse_query_from_json(json_val)
        llm_response = self._predict(llm_query)
        return jsonify(asdict(llm_response))

    @app.route(f'/llm/stream-predict', methods=['GET', 'POST'])
    def handle_stream_predict(self):
        json_val = request.get_json()
        print(json_val)
        llm_query = LLMPipeline.parse_query_from_json(json_val)

        def generate_output(q: LLMQuery):
            with app.app_context():
                for response, history, past_key_values in next(self._stream_predict(q)):
                    history = [Chat(role=chat['role'], content=chat['content']) for chat in history]
                    llm_response = LLMResponse(
                        response=response,
                        history=history
                    )
                    yield jsonify(llm_response).data + b'\n'

        return Response(stream_with_context(generate_output(llm_query)), content_type='application/json')
