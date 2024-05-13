from dataclasses import asdict

import torch
from flask import Flask, request, jsonify
from loguru import logger
from transformers import BlipProcessor, BlipForConditionalGeneration

from common import util
from common.datacls import ModelNameConst as SNR
from common.exc import img_cap_loading_log
from config import GLOBAL_CONFIG as G_CFG
from img_cap.pipeline import ImageCapPipeline, ImageCaptioningModelResponse, ImageCaptioningModelQuery

_app = Flask(__name__)

_host: str  # Host address for the Flask application
_port: int  # Port number for the Flask application
_debug: bool  # Debug mode flag for the Flask application
_processor: any
_model: any


@img_cap_loading_log
def init():
    global _host, _port, _debug, _processor, _model

    blip_cfg = G_CFG.image_captioning
    _host, _port, _debug = blip_cfg.host, blip_cfg.port, blip_cfg.debug
    model_path = blip_cfg.models[0].model_path

    _processor = BlipProcessor.from_pretrained(model_path)
    _model = BlipForConditionalGeneration.from_pretrained(model_path, torch_dtype=torch.float16).to("cuda")
    assert _processor and _model


def start():
    logger.info(f'👀 Application {SNR.BLIP} is starting...')
    _app.run(host=_host, port=_port, debug=_debug)
    logger.warning(f'⚠️ Application {SNR.BLIP} stopped.')


def _predict(query: ImageCaptioningModelQuery):
    raw_image = util.convert_base64_str_to_pil_image(query.img_data)

    # 条件式图片转字幕
    inputs = _processor(raw_image, query.prompt, return_tensors="pt").to("cuda", torch.float16)

    out = _model.generate(**inputs)
    output_text = _processor.decode(out[0], skip_special_tokens=True)

    return ImageCaptioningModelResponse(caption=output_text)


@_app.route(f'/image-captioning/predict', methods=['GET', "POST"])
def _handle_predict():
    logger.info('↘️ 请求接受：处理中……')
    query = ImageCapPipeline.parse_query_from_json(request.json)
    assert query.img_data, f"没有图片数据。"
    response = _predict(query)
    logger.info(f'✅ 模型响应：{response.caption}')
    return jsonify(asdict(response))
