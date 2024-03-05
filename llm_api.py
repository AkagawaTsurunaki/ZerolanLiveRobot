from flask import Flask, request, jsonify

from chatglm3 import core
from chatglm3.common import ModelRequest, ModelResponse
from chatglm3.service import handle_config, predict
from common import HttpResponseBody, Code, is_blank

app = Flask(__name__)

history = []


@app.route('/clear', methods=['GET'])
def handle_clear_history():
    """
    清除会话历史
    """
    global history
    history = []
    http_response_body = HttpResponseBody(
        code=Code.OK.value,
        msg="已清除会话历史"
    )
    return jsonify(http_response_body)


@app.route('/predict', methods=['POST'])
def handle_predict():
    """
    预测
    """
    global history

    data = request.get_json()
    model_req = ModelRequest(**data)

    if is_blank(model_req.query):
        http_response_body = HttpResponseBody(
            code=Code.BLANK_STRING.value,
            msg="Query 为空字符串"
        )
        return jsonify(http_response_body)

    if model_req.history is None:
        model_req.history = []

    if not (0. <= model_req.top_p <= 1.):
        http_response_body = HttpResponseBody(
            code=Code.INVALID_NUMBER.value,
            msg="Top-p 采样率应在 [0, 1] 这一区间内"
        )
        return jsonify(http_response_body)

    if not (0. <= model_req.temperature <= 1.):
        http_response_body = HttpResponseBody(
            code=Code.INVALID_NUMBER.value,
            msg="Temperature 应在 [0, 1] 这一区间内"
        )
        return jsonify(http_response_body)

    response, history = predict(model_req.sys_prompt + model_req.query, model_req.history, model_req.top_p,
                                model_req.temperature, True)

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
