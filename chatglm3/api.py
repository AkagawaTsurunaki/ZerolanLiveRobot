from dataclasses import dataclass, asdict

from flask import Flask, Response, jsonify, stream_with_context
from flask import request

import chatglm3.service as serv

app = Flask(__name__)


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


@app.route('/streampredict', methods=['POST'])
def handle_stream_output():
    model_req = ModelRequest(**request.json)

    def generate_output(model_req: ModelRequest):
        with app.app_context():
            for response, history, past_key_values in next(
                    serv.stream_predict(
                        query=model_req.sys_prompt + model_req.query,
                        history=model_req.history,
                        top_p=model_req.top_p,
                        temperature=model_req.temperature,
                        return_past_key_values=True
                    )
            ):
                model_resp = ModelResponse(response=response, history=history)
                yield jsonify(asdict(model_resp)).data + b'\n'

    return Response(stream_with_context(generate_output(model_req)), content_type='application/json')


def start():
    app.run('127.0.0.1', port=8085, debug=False)
