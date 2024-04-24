from dataclasses import asdict

from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoModel

from llm.pipeline import LLMPipeline
from utils.datacls import LLMResponse, Chat, LLMQuery

app = Flask(__name__)

# Model names: "Qwen/Qwen-7B-Chat", "Qwen/Qwen-14B-Chat"
TOKENIZER: AutoTokenizer
MODEL: AutoModelForCausalLM | AutoModel


def _predict(llm_query: LLMQuery):
    query = llm_query.text
    history = llm_query.history
    history = [{'role': chat.role, 'content': chat.content} for chat in history]
    response, history = MODEL.chat(TOKENIZER, query, history=history)
    history = [Chat(role=chat['role'], content=chat['content']) for chat in history]
    llm_response = LLMResponse(response=response, history=history)
    return llm_response


@app.route('/llm/predict', methods=['GET', 'POST'])
def handle_predict():
    json_val = request.get_json()
    llm_query = LLMPipeline.convert_query_from_json(json_val)
    llm_response = _predict(llm_query)
    return jsonify(asdict(llm_response))


@app.route('/llm/stream-predict', methods=['GET', 'POST'])
def handle_predict():
    raise NotImplementedError('This route has not been implemented yet.')


def start(model_path, mode, host, port, debug):
    global MODEL, TOKENIZER
    # Load model on given mode
    if mode == 'bf16':
        MODEL = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto", trust_remote_code=True,
                                                     bf16=True).eval()
    elif mode == 'fp16':
        MODEL = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto", trust_remote_code=True,
                                                     fp16=True).eval()
    elif mode == 'cpu':
        MODEL = AutoModelForCausalLM.from_pretrained(model_path, device_map="cpu", trust_remote_code=True).eval()
    else:
        MODEL = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto", trust_remote_code=True).eval()

        # Load auto tokenizer
    TOKENIZER = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)

    # Specify hyperparameters for generation. But if you use transformers>=4.32.0, there is no need to do this.
    # model.generation_config = GenerationConfig.from_pretrained("Qwen/Qwen-7B-Chat", trust_remote_code=True)

    # Run application
    app.run(host=host, port=port, debug=debug)
