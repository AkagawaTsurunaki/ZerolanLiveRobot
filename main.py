# import json
# import threading
#
# import requests
# from flask import request, Flask, jsonify
# from loguru import logger
# from bilibili import service
# from audio_player2 import AudioPlayer
# from common import HttpResponseBody, Code, is_blank, ModelResponse
# from global_config import CentralControllerConfig
# from gptsovits import service
#
# app = Flask(__name__)
# global_audio_player = AudioPlayer()
#
#
# def remove_newlines(text):
#     cleaned_text = text.replace('\n', '').replace('\r', '')
#     return cleaned_text
#
#
# def is_audio_player_empty():
#     return global_audio_player.is_empty()
#
#
# @app.route('/query', methods=['POST'])
# def handle_query_4_llm_gptsovits():
#     """
#     {
#         sys_prompt: str
#         query: str
#         history: list
#         top_p: float
#         temperature: float
#     }
#
#     :return:
#     """
#     model_req_json = request.get_json()
#
#     # 访问模型地址，将响应体解析为 Python 类
#     response = requests.post("http://127.0.0.1:8721/predict", json=model_req_json)
#     json_dict = json.loads(response.content)
#     model_resp_dict = HttpResponseBody(**json_dict).data
#     model_resp = ModelResponse(**model_resp_dict)
#     # 访问语音合成模型地址，将
#     sentence_list = model_resp.response.splitlines()
#     for sentence in sentence_list:
#         if is_blank(sentence):
#             continue
#         # 预先对模型的文段进行清理，删除换行符
#         sentence = remove_newlines(sentence)
#         tmp_wav_file_path = gpt_sovits_api.predict(sentence, 'zh')
#         global_audio_player.add(text=sentence, wav_file_path=tmp_wav_file_path)
#
#     logger.info("控制器执行了一次从 ChatGLM3 到 GPT-SoVITS 的推理过程")
#     return jsonify(HttpResponseBody(
#         code=Code.OK.value,
#         msg="控制器执行了一次从 ChatGLM3 到 GPT-SoVITS 的推理过程"
#     ))
#
#
# if __name__ == '__main__':
#     audio_player_thread = threading.Thread(target=global_audio_player.start)
#     manager_thread = threading.Thread(target=live_dnmk_mng.start)
#     audio_player_thread.start()
#     manager_thread.start()
#
#     app.run(host=CentralControllerConfig.host, port=CentralControllerConfig.port, debug=False)
#     # 不要删除这里
#
#     audio_player_thread.join()
#     manager_thread.join()
