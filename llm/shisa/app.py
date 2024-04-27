"""
More detail, please see:
https://huggingface.co/augmxnt/shisa-7b-v1
"""
import copy
from dataclasses import asdict

import torch
from flask import Flask, request, jsonify
from transformers import AutoTokenizer, AutoModelForCausalLM, TextStreamer

from common.abs_app import AbstractApp
from config import GlobalConfig
from llm.pipeline import LLMPipeline
from common.datacls import LLMQuery, LLMResponse, Chat, Role

app = Flask(__name__)


class ShisaApp(AbstractApp):

    def __init__(self, cfg: GlobalConfig):
        super().__init__()
        self.host = cfg.large_language_model.host
        self.host.port = cfg.large_language_model.port
        self.debug = cfg.large_language_model.debug
        model_path = cfg.large_language_model.models[0].model_path
        self._tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=True)
        self._model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16,
        ).to('cuda')
        self._streamer = TextStreamer(self._tokenizer, skip_prompt=True)

    def start(self):
        app.run(host=self.host, port=self.port, debug=self.debug)

    def _predict(self, llm_query: LLMQuery):
        assert len(llm_query.history) > 0 and llm_query.history[0].role == Role.SYSTEM, f'Must includes system prompt'

        llm_query_history = copy.deepcopy(llm_query.history)
        llm_query_history.append(Chat(role=Role.USER, content=llm_query.text))
        history = [{"role": chat.role, "content": chat.content} for chat in llm_query_history]

        inputs = self._tokenizer.apply_chat_template(history, add_generation_prompt=True, return_tensors="pt")
        first_param_device = next(self._model.parameters()).device
        inputs = inputs.to(first_param_device)

        with torch.no_grad():
            outputs = self._model.generate(
                inputs,
                pad_token_id=self._tokenizer.eos_token_id,
                max_new_tokens=500,
                temperature=0.5,
                repetition_penalty=1.15,
                top_p=0.95,
                do_sample=True,
                streamer=self._streamer,
            )

        new_tokens = outputs[0, inputs.size(1):]
        response = self._tokenizer.decode(new_tokens, skip_special_tokens=True)
        llm_query.history.append(Chat(role=Role.ASSISTANT, content=response))
        return LLMResponse(response=response, history=llm_query.history)

    @app.route('/llm/predict', methods=['POST', 'GET'])
    def handle_predict(self):
        json_val = request.get_json()
        llm_query = LLMPipeline.parse_query_from_json(json_val)
        llm_response = self._predict(llm_query)
        return jsonify(asdict(llm_response))

    @app.route('/llm/stream-predict', methods=['GET', 'POST'])
    def handle_predict(self):
        raise NotImplementedError('This route has not been implemented yet.')
