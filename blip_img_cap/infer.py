import os.path

import torch
import yaml
from PIL import Image
from loguru import logger
from transformers import BlipProcessor, BlipForConditionalGeneration


def load_config():
    with open(file='blip_img_cap/config.yaml', mode='r', encoding='utf-8') as file:
        config: dict = yaml.safe_load(file)
        config = config.get('BlipImageCaptioningLargeConfig')
        if config:
            model_path = config.get('model_path')
            if os.path.exists(model_path):
                return model_path
        return 'Salesforce/blip-image-captioning-large'


logger.info('正在读取 blip-image-captioning-large 模型的配置文件')
MODEL_PATH = load_config()

logger.info('正在加载模型 blip-image-captioning-large')

processor = BlipProcessor.from_pretrained(MODEL_PATH)
model = BlipForConditionalGeneration.from_pretrained(MODEL_PATH, torch_dtype=torch.float16).to("cuda")

logger.info('模型 blip-image-captioning-large 加载完毕')


def infer_by_path(img_path: str, text: str = "a photography of"):
    raw_image = Image.open(img_path).convert('RGB')

    # conditional image captioning
    inputs = processor(raw_image, text, return_tensors="pt").to("cuda", torch.float16)

    out = model.generate(**inputs)
    output_text = processor.decode(out[0], skip_special_tokens=True)
    return output_text


def infer(img, text: str = "a photography of"):
    raw_image = img.convert('RGB')
    # conditional image captioning
    inputs = processor(raw_image, text, return_tensors="pt").to("cuda", torch.float16)

    out = model.generate(**inputs)
    output_text = processor.decode(out[0], skip_special_tokens=True)
    return output_text
