import json
from dataclasses import asdict

import requests
from flask import Flask, Response, jsonify, stream_with_context, request

from chatglm3.service import ChatGLM3Service

app = Flask(__name__)

from dataclasses import dataclass

llm_serv: ChatGLM3Service


@dataclass
class ModelRequest:
    sys_prompt: str
    query: str
    history: list
    top_p: float
    temperature: float


@dataclass
class ModelResponse:
    response: str
    history: list[dict]


@app.route('/predict', methods=['POST'])
def stream_llm_output():
    model_req = ModelRequest(**request.json)

    def generate_output(model_req: ModelRequest):
        with app.app_context():
            for response, history, past_key_values in next(
                    llm_serv.stream_predict(
                        query=model_req.sys_prompt + model_req.query,
                        history=model_req.history,
                        top_p=model_req.top_p,
                        temperature=model_req.temperature,
                        return_past_key_values=True
                    )
            ):
                model_resp = ModelResponse(response=response, history=history)
                print(model_resp.response)
                yield jsonify(asdict(model_resp)).data

    return Response(stream_with_context(generate_output(model_req)), content_type='application/json')


# if __name__ == '__main__':
def run_api():
    # Warning: 启动 debug 模式会导致模型被加载两次，请注意这一点。
    global llm_serv
    llm_serv = ChatGLM3Service()
    app.run(host=llm_serv.HOST, port=llm_serv.PORT, debug=llm_serv.DEBUG)


def quick_chat(query: str):
    model_req = ModelRequest(
        query=query,
        history=[],
        temperature=1.,
        top_p=1.,
        sys_prompt=''
    )
    response = requests.post('http://127.0.0.1:8721/predict', json=asdict(model_req))
    model_resp = ModelResponse(**(response.json()))
    return model_resp.response


def stream_chat(model_req: ModelRequest):
    response = requests.post('http://127.0.0.1:8721/predict', stream=True, json=asdict(model_req))

    for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
        if chunk:
            # try:
            json_value = json.loads(chunk, strict=False)
            # except Exception as e:
            #     continue

            yield ModelResponse(**json_value)
