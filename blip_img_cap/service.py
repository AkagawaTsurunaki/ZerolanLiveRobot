from dataclasses import asdict
from os import PathLike

import torch
from PIL import Image
from flask import Flask, request, jsonify
from loguru import logger
from transformers import BlipProcessor, BlipForConditionalGeneration

from utils.datacls import HTTPResponseBody

app = Flask(__name__)

# 该服务是否已被初始化?
g_is_service_inited = False

# 该服务是否正在运行?
g_is_service_running = False

# 系统提示词
g_sys_prompt: str = ''

PROCESSOR: BlipProcessor
MODEL: BlipForConditionalGeneration


def init(model_path: str | PathLike, text_prompt: str):
    logger.info('👀 模型 blip-image-captioning-large 正在加载……')

    global PROCESSOR, MODEL, g_sys_prompt, g_is_service_inited, g_is_service_running
    g_sys_prompt = text_prompt
    PROCESSOR = BlipProcessor.from_pretrained(model_path)
    MODEL = BlipForConditionalGeneration.from_pretrained(model_path, torch_dtype=torch.float16).to("cuda")
    assert PROCESSOR and MODEL, f'❌️ 模型 blip-image-captioning-large 加载失败'
    g_is_service_inited = True
    g_is_service_running = True
    logger.info('👀 模型 blip-image-captioning-large 加载完毕')
    return g_is_service_inited


def infer_by_path(img_path: str, text: str = g_sys_prompt):
    assert g_is_service_inited, f'❌️ blip-image-captioning-large 服务未初始化'
    raw_image = Image.open(img_path).convert('RGB')

    # conditional image captioning
    inputs = PROCESSOR(raw_image, text, return_tensors="pt").to("cuda", torch.float16)

    out = MODEL.generate(**inputs)
    output_text = PROCESSOR.decode(out[0], skip_special_tokens=True)
    return output_text


@app.route('/blip/infer', methods=['GET'])
def handle_blip_infer():
    req = request.json
    img_path = req['img_path']
    prompt = req['prompt']
    caption = infer_by_path(img_path, prompt)
    response = HTTPResponseBody(ok=True, msg='推理完成', data={'caption': caption})
    return jsonify(asdict(response))


def start():
    app.run(host='127.0.0.1', port=5926, debug=False)
