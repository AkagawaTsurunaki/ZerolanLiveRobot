import json

import requests
from flask import request, Flask, jsonify
from loguru import logger
from playsound import playsound

import gpt_sovits_api
from chatglm3.common import ModelResponse
from common import HttpResponseBody, Code

app = Flask(__name__)


@app.route('/query', methods=['POST'])
def handle_query_4_llm_gptsovits():
    """
    {
        sys_prompt: str
        query: str
        history: list
        top_p: float
        temperature: float
    }


    :return:
    """
    model_req_json = request.get_json()
    # 访问模型地址，将响应体解析为 Python 类
    response = requests.post("http://127.0.0.1:8721/predict", json=model_req_json)
    json_dict = json.loads(response.content)
    model_resp_dict = HttpResponseBody(**json_dict).data
    model_resp = ModelResponse(**model_resp_dict)
    # 访问语音合成模型地址，将

    tmp_wav_file_path = gpt_sovits_api.predict(model_resp.response, 'zh')
    block = True
    logger.info('正在以' + "阻塞" if block else "非阻塞" + f'模式播放音频文件：{tmp_wav_file_path}')
    playsound(tmp_wav_file_path, block=block)
    logger.info(f'音频文件播放完毕：{tmp_wav_file_path}')

    logger.info("控制器执行了一次从 ChatGLM3 到 GPT-SoVITS 的推理过程")
    return jsonify(HttpResponseBody(
        code=Code.OK.value,
        msg="控制器执行了一次从 ChatGLM3 到 GPT-SoVITS 的推理过程"
    ))


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=10020, debug=False)
