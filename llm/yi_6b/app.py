import argparse
from dataclasses import asdict

from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer

from llm.pipeline import LLMPipeline
from utils.datacls import NewLLMQuery, NewLLMResponse, Role, Chat

app = Flask(__name__)

TOKENIZER: AutoTokenizer

# Since transformers 4.35.0, the GPT-Q/AWQ model can be loaded using AutoModelForCausalLM.
MODEL: AutoModelForCausalLM


def _predict(llm_query: NewLLMQuery):
    messages = [{"role": chat.role, "content": chat.content} for chat in llm_query.history]
    messages.append({"role": Role.USER, "content": llm_query.text})
    input_ids = TOKENIZER.apply_chat_template(conversation=messages, tokenize=True, add_generation_prompt=True,
                                              return_tensors='pt')
    output_ids = MODEL.generate(input_ids.to('cuda'))
    response = TOKENIZER.decode(output_ids[0][input_ids.shape[1]:], skip_special_tokens=True)
    messages.append({"role": Role.ASSISTANT, "content": response})
    history = [Chat(role=chat['role'], content=chat['content']) for chat in messages]
    return NewLLMResponse(response, history)


@app.route('/01-ai/Yi/predict', methods=['GET', 'POST'])
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
    parser.add_argument('--port', '-p', type=int, default=9881)
    parser.add_argument('--debug', '-d', type=str, default=False)

    model_path, mode, host, port, debug = parser.parse_args()

    TOKENIZER = AutoTokenizer.from_pretrained(model_path, use_fast=False)
    MODEL = AutoModelForCausalLM.from_pretrained(
        model_path,
        device_map=mode,
        torch_dtype='auto'
    ).eval()
