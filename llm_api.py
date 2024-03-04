from flask import Flask, request, jsonify

from chatglm3 import core
from chatglm3.common import ModelRequest, ModelResponse
from chatglm3.core import predict
from chatglm3.service import handle_config
from common import HttpResponseBody, Code

app = Flask(__name__)


@app.route('/predict', methods=['POST'])
def handle_request():
    data = request.get_json()
    req = ModelRequest(**data)

    response, history = predict(req.query, req.history, req.top_p, req.temperature, True)

    http_response_body = HttpResponseBody(
        code=Code.OK.value,
        msg="推理成功",
        data=ModelResponse(response=response, history=history)
    )

    return jsonify(http_response_body)


if __name__ == '__main__':
    config = handle_config()
    core.init(tokenizer_path=config.tokenizer_path, model_path=config.model_path, quantize=config.quantize)
    app.run(config.host, config.port, config.debug)
