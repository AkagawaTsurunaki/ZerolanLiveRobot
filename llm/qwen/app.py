from dataclasses import asdict

from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer

from common.abs_app import AbstractApp
from config import GlobalConfig
from llm.pipeline import LLMPipeline
from utils.datacls import LLMResponse, Chat, LLMQuery

app = Flask(__name__)


# Model names: "Qwen/Qwen-7B-Chat", "Qwen/Qwen-14B-Chat"
class QwenApp(AbstractApp):
    def __init__(self, cfg: GlobalConfig):
        super().__init__()
        self.host = cfg.large_language_model.host
        self.host.port = cfg.large_language_model.port
        self.debug = cfg.large_language_model.debug
        qwen_cfg = cfg.large_language_model.models[0]
        self._mode = qwen_cfg.loading_mode
        self._model_path = qwen_cfg.model_path
        # Load model on given mode
        if self._mode == 'bf16':
            self._model = AutoModelForCausalLM.from_pretrained(self._model_path, device_map="auto",
                                                               trust_remote_code=True,
                                                               bf16=True).eval()
        elif self._mode == 'fp16':
            self._model = AutoModelForCausalLM.from_pretrained(self._model_path, device_map="auto",
                                                               trust_remote_code=True,
                                                               fp16=True).eval()
        elif self._mode == 'cpu':
            self._model = AutoModelForCausalLM.from_pretrained(self._model_path, device_map="cpu",
                                                               trust_remote_code=True).eval()
        else:
            self._model = AutoModelForCausalLM.from_pretrained(self._model_path, device_map="auto",
                                                               trust_remote_code=True).eval()

        # Load auto tokenizer
        self._tokenizer = AutoTokenizer.from_pretrained(self._model_path, trust_remote_code=True)

    def start(self):
        # Run application
        app.run(host=self.host, port=self.port, debug=self.debug)

    def _predict(self, llm_query: LLMQuery):
        query = llm_query.text
        history = llm_query.history
        history = [{'role': chat.role, 'content': chat.content} for chat in history]
        response, history = self._model.chat(self._tokenizer, query, history=history)
        history = [Chat(role=chat['role'], content=chat['content']) for chat in history]
        llm_response = LLMResponse(response=response, history=history)
        return llm_response

    @app.route('/llm/predict', methods=['GET', 'POST'])
    def handle_predict(self):
        json_val = request.get_json()
        llm_query = LLMPipeline.parse_query_from_json(json_val)
        llm_response = self._predict(llm_query)
        return jsonify(asdict(llm_response))

    @app.route('/llm/stream-predict', methods=['GET', 'POST'])
    def handle_stream_predict(self):
        raise NotImplementedError('This route has not been implemented yet.')
