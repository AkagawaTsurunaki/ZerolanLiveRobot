import os
from dataclasses import asdict

import torch
from PIL import Image
from flask import Flask, request, jsonify
from loguru import logger
from transformers import BlipProcessor, BlipForConditionalGeneration

from common.datacls import ModelNameConst as SNR
from config import GlobalConfig
from img_cap.pipeline import ImageCapPipeline, ImageCaptioningModelResponse, ImageCaptioningModelQuery

_app = Flask(__name__)

_host: str  # Host address for the Flask application
_port: int  # Port number for the Flask application
_debug: bool  # Debug mode flag for the Flask application
_processor: any
_model: any


def init(cfg: GlobalConfig):
    logger.info(f'👀 Application {SNR.BLIP} is initializing...')
    global _host, _port, _debug, _processor, _model

    blip_cfg = cfg.image_captioning
    _host, _port, _debug = blip_cfg.host, blip_cfg.port, blip_cfg.debug
    model_path = blip_cfg.models[0].model_path

    logger.info(f'👀 Model {SNR.BLIP} is loading...')
    _processor = BlipProcessor.from_pretrained(model_path)
    _model = BlipForConditionalGeneration.from_pretrained(model_path, torch_dtype=torch.float16).to("cuda")
    assert _processor and _model, f'❌️ Model {SNR.BLIP} failed to load.'
    logger.info(f'👀 Model {SNR.BLIP} loaded successfully.')

    logger.info(f'👀 Application {SNR.BLIP} initialized successfully.')


def start():
    logger.info(f'👀 Application {SNR.BLIP} is starting...')
    _app.run(host=_host, port=_port, debug=_debug)
    logger.warning(f'👀 Application {SNR.BLIP} stopped.')


def _predict(query: ImageCaptioningModelQuery):
    raw_image = Image.open(query.img_path).convert('RGB')

    # conditional image captioning
    inputs = _processor(raw_image, query.prompt, return_tensors="pt").to("cuda", torch.float16)

    out = _model.generate(**inputs)
    output_text = _processor.decode(out[0], skip_special_tokens=True)

    return ImageCaptioningModelResponse(caption=output_text)


@_app.route(f'/image-captioning/predict', methods=['GET'])
def _handle_predict():
    query = ImageCapPipeline.parse_query_from_json(request.json)
    assert os.path.exists(query.img_path), f'Can not find image file: "{query.img_path}"'
    response = _predict(query)
    return jsonify(asdict(response))
