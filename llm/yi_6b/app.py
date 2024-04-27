from dataclasses import asdict

from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer

from common.abs_app import AbstractApp
from config import GlobalConfig
from llm.pipeline import LLMPipeline
from common.datacls import LLMQuery, LLMResponse, Role, Chat

app = Flask(__name__)


class YiApp(AbstractApp):
    def __init__(self, cfg: GlobalConfig):
        super().__init__()
        self.host = cfg.large_language_model.host
        self.host.port = cfg.large_language_model.port
        self.debug = cfg.large_language_model.debug

        model_path = cfg.large_language_model.models[0].model_path
        mode = cfg.large_language_model.models[0].loading_mode
        self._tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=False)
        # Since transformers 4.35.0, the GPT-Q/AWQ model can be loaded using AutoModelForCausalLM.
        self._tokenizer = AutoModelForCausalLM.from_pretrained(
            model_path,
            device_map=mode,
            torch_dtype='auto'
        ).eval()

    def start(self):
        app.run(host=self.host, port=self.port, debug=self.debug)

    def _predict(self, llm_query: LLMQuery):
        messages = [{"role": chat.role, "content": chat.content} for chat in llm_query.history]
        messages.append({"role": Role.USER, "content": llm_query.text})
        input_ids = self._tokenizer.apply_chat_template(conversation=messages, tokenize=True,
                                                        add_generation_prompt=True,
                                                        return_tensors='pt')
        output_ids = self._tokenizer.generate(input_ids.to('cuda'))
        response = self._tokenizer.decode(output_ids[0][input_ids.shape[1]:], skip_special_tokens=True)
        messages.append({"role": Role.ASSISTANT, "content": response})
        history = [Chat(role=chat['role'], content=chat['content']) for chat in messages]
        return LLMResponse(response, history)

    @app.route('/llm/predict', methods=['GET', 'POST'])
    def handle_predict(self):
        json_val = request.get_json()
        llm_query = LLMPipeline.parse_query_from_json(json_val)
        llm_response = self._predict(llm_query)
        return jsonify(asdict(llm_response))

    @app.route('/llm/stream-predict', methods=['GET', 'POST'])
    def handle_predict(self):
        raise NotImplementedError('This route has not been implemented yet.')
