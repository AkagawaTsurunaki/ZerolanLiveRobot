from os import PathLike

import torch
from PIL import Image
from loguru import logger
from transformers import BlipProcessor, BlipForConditionalGeneration, ProcessorMixin

is_initialized = False

processor: BlipProcessor
model: BlipForConditionalGeneration
sys_prompt = ''


def init(model_path: str | PathLike, text_prompt: str):
    logger.info('👀 模型 blip-image-captioning-large 正在加载……')

    global processor, model, sys_prompt, is_initialized
    sys_prompt = text_prompt
    processor = BlipProcessor.from_pretrained(model_path)
    model = BlipForConditionalGeneration.from_pretrained(model_path, torch_dtype=torch.float16).to("cuda")
    assert processor and model, f'❌️ 模型 blip-image-captioning-large 加载失败'
    is_initialized = True

    logger.info('👀 模型 blip-image-captioning-large 加载完毕')
    return is_initialized


def infer_by_path(img_path: str, text: str = sys_prompt):
    assert is_initialized, f'❌️ blip-image-captioning-large 服务未初始化'
    raw_image = Image.open(img_path).convert('RGB')

    # conditional image captioning
    inputs = processor(raw_image, text, return_tensors="pt").to("cuda", torch.float16)

    out = model.generate(**inputs)
    output_text = processor.decode(out[0], skip_special_tokens=True)
    return output_text


def infer(img, text: str = "a photography of"):
    assert is_initialized, f'❌️ blip-image-captioning-large 服务未初始化'
    raw_image = img.convert('RGB')
    # conditional image captioning
    inputs = processor(raw_image, text, return_tensors="pt").to("cuda", torch.float16)

    out = model.generate(**inputs)
    output_text = processor.decode(out[0], skip_special_tokens=True)
    return output_text
