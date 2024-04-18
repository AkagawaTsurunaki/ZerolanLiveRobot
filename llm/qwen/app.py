import argparse
from dataclasses import asdict

from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoModel

from llm.pipeline import LLMPipeline
from utils.datacls import NewLLMResponse, Chat, NewLLMQuery

app = Flask(__name__)

# Model names: "Qwen/Qwen-7B-Chat", "Qwen/Qwen-14B-Chat"
tokenizer: AutoTokenizer
model: AutoModelForCausalLM | AutoModel


def _predict(llm_query: NewLLMQuery):
    query = llm_query.text
    history = llm_query.history
    history = [{'role': chat.role, 'content': chat.content} for chat in history]
    response, history = model.chat(tokenizer, query, history=history)
    history = [Chat(role=chat['role'], content=chat['content']) for chat in history]
    llm_response = NewLLMResponse(response=response, history=history)
    return llm_response


@app.route('/Qwen/Qwen-7B-Chat/predict', methods=['GET', 'POST'])
def handle_predict():
    json_val = request.get_json()
    llm_query = LLMPipeline.convert_query_from_json(json_val)
    llm_response = _predict(llm_query)
    return jsonify(asdict(llm_response))


if __name__ == '__main__':

    # Parse arguments
    parser = argparse.ArgumentParser()

    parser.add_argument('--model-path', '-mp', type=str, default="Qwen/Qwen-7B-Chat")
    parser.add_argument('--loading-mode', '-lm', type=str, default='auto')
    parser.add_argument('--host', '-h', type=str, default='127.0.0.1')
    parser.add_argument('--port', '-p', type=int, default=12556)
    parser.add_argument('--debug', '-d', type=str, default=False)

    model_path, mode, host, port, debug = parser.parse_args()

    # Load model on given mode
    if mode == 'bf16':
        model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto", trust_remote_code=True,
                                                     bf16=True).eval()
    elif mode == 'fp16':
        model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto", trust_remote_code=True,
                                                     fp16=True).eval()
    elif mode == 'cpu':
        model = AutoModelForCausalLM.from_pretrained(model_path, device_map="cpu", trust_remote_code=True).eval()
    else:
        model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto", trust_remote_code=True).eval()

    # Load auto tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)

    # Specify hyperparameters for generation. But if you use transformers>=4.32.0, there is no need to do this.
    # model.generation_config = GenerationConfig.from_pretrained("Qwen/Qwen-7B-Chat", trust_remote_code=True)

    # Run application
    app.run(host=host, port=port, debug=False)
