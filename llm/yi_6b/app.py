from dataclasses import asdict

from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer

from llm.pipeline import LLMPipeline
from utils.datacls import LLMQuery, LLMResponse, Role, Chat

app = Flask(__name__)

TOKENIZER: AutoTokenizer

# Since transformers 4.35.0, the GPT-Q/AWQ model can be loaded using AutoModelForCausalLM.
MODEL: AutoModelForCausalLM


def _predict(llm_query: LLMQuery):
    messages = [{"role": chat.role, "content": chat.content} for chat in llm_query.history]
    messages.append({"role": Role.USER, "content": llm_query.text})
    input_ids = TOKENIZER.apply_chat_template(conversation=messages, tokenize=True, add_generation_prompt=True,
                                              return_tensors='pt')
    output_ids = MODEL.generate(input_ids.to('cuda'))
    response = TOKENIZER.decode(output_ids[0][input_ids.shape[1]:], skip_special_tokens=True)
    messages.append({"role": Role.ASSISTANT, "content": response})
    history = [Chat(role=chat['role'], content=chat['content']) for chat in messages]
    return LLMResponse(response, history)


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
    global TOKENIZER, MODEL

    TOKENIZER = AutoTokenizer.from_pretrained(model_path, use_fast=False)
    MODEL = AutoModelForCausalLM.from_pretrained(
        model_path,
        device_map=mode,
        torch_dtype='auto'
    ).eval()

    app.run(host=host, port=port, debug=debug)
