import os
from dataclasses import asdict

import torch
from PIL import Image
from flask import Flask, request, jsonify
from loguru import logger
from transformers import BlipProcessor, BlipForConditionalGeneration

from common.datacls import ServiceNameConst as SNR
from config import GlobalConfig
from img_cap.pipeline import ImageCapPipeline, ImageCapResponse, ImageCapQuery

_app = Flask(__name__)
_host: str  # Host address for the Flask application
_port: int  # Port number for the Flask application
_debug: bool  # Debug mode flag for the Flask application
processor: any
model: any


def init(cfg: GlobalConfig):
    global _host, _port, _debug, processor, model

    _host = cfg.image_captioning.host
    _port = cfg.image_captioning.port
    _debug = cfg.image_captioning.debug

    blip_cfg = cfg.image_captioning
    model_path = blip_cfg.models[0].model_path
    logger.info(f'👀 Model {SNR.BLIP} is loading...')
    processor = BlipProcessor.from_pretrained(model_path)
    model = BlipForConditionalGeneration.from_pretrained(model_path, torch_dtype=torch.float16).to("cuda")
    logger.info(f'👀 Model {SNR.BLIP} loaded successfully.')


def start():
    _app.run(host=_host, port=_port, debug=_debug)


def _predict(query: ImageCapQuery):
    raw_image = Image.open(query.img_path).convert('RGB')

    # conditional image captioning
    inputs = processor(raw_image, query.prompt, return_tensors="pt").to("cuda", torch.float16)

    out = model.generate(**inputs)
    output_text = processor.decode(out[0], skip_special_tokens=True)

    return ImageCapResponse(caption=output_text)


@_app.route(f'/image-captioning/predict', methods=['GET'])
def _handle_predict():
    query = ImageCapPipeline.parse_query_from_json(request.json)
    assert os.path.exists(query.img_path), f'Can not find image file: "{query.img_path}"'
    response = _predict(query)
    return jsonify(asdict(response))
