import os
from dataclasses import asdict

import torch
from PIL import Image
from flask import Flask, request, jsonify
from loguru import logger
from transformers import BlipProcessor, BlipForConditionalGeneration

from common.abs_app import AbstractApp
from config import ImageCaptioningConfig
from img_cap.pipeline import ImageCapPipeline, ImageCapResponse, ImageCapQuery
from common.datacls import ServiceNameConst as SNR

app = Flask(__name__)


class BlipApp(AbstractApp):

    def __init__(self, cfg: ImageCaptioningConfig):
        super().__init__()
        self._model_path = cfg.models[0].model_path
        self._host: str = cfg.host
        self._port: int = cfg.port
        self._debug: bool = cfg.debug
        logger.info(f'👀 Model {SNR.BLIP} is loading...')
        self._processor: BlipProcessor = BlipProcessor.from_pretrained(self._model_path)
        self._model: BlipForConditionalGeneration = BlipForConditionalGeneration.from_pretrained(self._model_path,
                                                                                                 torch_dtype=torch.float16).to(
            "cuda")
        logger.info(f'👀 Model {SNR.BLIP} loaded successfully.')
        self._img_cap_pipeline = ImageCapPipeline(cfg)

    def start(self):
        app.run(host=self._host, port=self._port, debug=self._debug)

    @app.route(f'/image-captioning/predict', methods=['GET'])
    def handle_predict(self):
        query = ImageCapPipeline.parse_query_from_json(request.json)
        assert os.path.exists(query.img_path), f'Can not find image file: "{query.img_path}"'
        response = self._predict(query)
        return jsonify(asdict(response))

    def _predict(self, query: ImageCapQuery):
        raw_image = Image.open(query.img_path).convert('RGB')

        # conditional image captioning
        inputs = self._processor(raw_image, query.prompt, return_tensors="pt").to("cuda", torch.float16)

        out = self._model.generate(**inputs)
        output_text = self._processor.decode(out[0], skip_special_tokens=True)

        return ImageCapResponse(caption=output_text)
