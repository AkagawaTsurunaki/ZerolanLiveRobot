import os
from dataclasses import asdict

import torch
from PIL import Image
from flask import Flask, request, jsonify
from loguru import logger
from transformers import BlipProcessor, BlipForConditionalGeneration

import initzr
from config.global_config import BlipImageCaptioningLargeConfig
from utils.datacls import HTTPResponseBody

app = Flask(__name__)

PROCESSOR: BlipProcessor
MODEL: BlipForConditionalGeneration


@app.route('/blip/infer', methods=['GET'])
def handle_blip_infer():
    req = request.json
    img_path = req.get('img_path', None)
    if not os.path.exists(img_path):
        response = HTTPResponseBody(ok=False, msg='图片路径不存在')
        return jsonify(asdict(response))
    prompt = req.get('prompt', None)
    caption = _infer_by_path(img_path, prompt)
    response = HTTPResponseBody(ok=True, msg='Blip 推理成功', data={'caption': caption})
    return jsonify(asdict(response))


def _infer_by_path(img_path: str, text: str):
    raw_image = Image.open(img_path).convert('RGB')

    # conditional image captioning
    inputs = PROCESSOR(raw_image, text, return_tensors="pt").to("cuda", torch.float16)

    out = MODEL.generate(**inputs)
    output_text = PROCESSOR.decode(out[0], skip_special_tokens=True)
    return output_text


def _init(config: BlipImageCaptioningLargeConfig):
    logger.info('👀 模型 blip-image-captioning-large 正在加载……')
    global PROCESSOR, MODEL
    initzr.load_blip_image_captioning_large_config()
    PROCESSOR = BlipProcessor.from_pretrained(config.model_path)
    MODEL = BlipForConditionalGeneration.from_pretrained(config.model_path, torch_dtype=torch.float16).to("cuda")
    assert PROCESSOR and MODEL, f'❌️ 模型 blip-image-captioning-large 加载失败'
    logger.info('👀 模型 blip-image-captioning-large 加载完毕')


def start():
    config = initzr.load_blip_image_captioning_large_config()
    _init(config)
    app.run(host=config.host, port=config.port, debug=config.debug)
