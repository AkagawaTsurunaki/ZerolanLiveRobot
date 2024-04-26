import os
from dataclasses import asdict

import torch
from PIL import Image
from flask import Flask, request, jsonify
from loguru import logger
from transformers import BlipProcessor, BlipForConditionalGeneration

from utils.datacls import HTTPResponseBody, ServiceNameConst as SNR

app = Flask(__name__)

PROCESSOR: BlipProcessor
MODEL: BlipForConditionalGeneration


@app.route(f'/image-captioning/predict', methods=['GET'])
def handle_blip_infer():
    req = request.json
    img_path = req.get('img_path', None)
    if not os.path.exists(img_path):
        response = HTTPResponseBody(ok=False, msg='Image path does not exist.')
        return jsonify(asdict(response))
    prompt = req.get('prompt', None)
    caption = _infer_by_path(img_path, prompt)
    response = HTTPResponseBody(ok=True, msg=f'{SNR.BLIP} predicted successfully.', data={'caption': caption})
    return jsonify(asdict(response))


def _infer_by_path(img_path: str, text: str):
    raw_image = Image.open(img_path).convert('RGB')

    # conditional image captioning
    inputs = PROCESSOR(raw_image, text, return_tensors="pt").to("cuda", torch.float16)

    out = MODEL.generate(**inputs)
    output_text = PROCESSOR.decode(out[0], skip_special_tokens=True)
    return output_text


def start(model_path, host, port, debug):
    global PROCESSOR, MODEL

    logger.info(f'👀 Model {SNR.BLIP} is loading...')
    PROCESSOR = BlipProcessor.from_pretrained(model_path)
    MODEL = BlipForConditionalGeneration.from_pretrained(model_path, torch_dtype=torch.float16).to("cuda")
    assert PROCESSOR and MODEL, f'❌️ Model {SNR.BLIP} loaded failed.'
    logger.info(f'👀 Model {SNR.BLIP} loaded successfully.')
    app.run(host=host, port=port, debug=debug)
