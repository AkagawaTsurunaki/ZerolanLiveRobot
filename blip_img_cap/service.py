from os import PathLike

import torch
from PIL import Image
from loguru import logger
from transformers import BlipProcessor, BlipForConditionalGeneration

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


def stop():
    global PROCESSOR, MODEL, g_is_service_inited, g_is_service_running, g_sys_prompt
    g_is_service_inited = False
    g_is_service_running = False
    PROCESSOR = None
    MODEL = None
    g_sys_prompt = None
    logger.warning('👀 模型 blip-image-captioning-large 服务已终止')
    return not g_is_service_running


def infer_by_path(img_path: str, text: str = g_sys_prompt):
    assert g_is_service_inited, f'❌️ blip-image-captioning-large 服务未初始化'
    raw_image = Image.open(img_path).convert('RGB')

    # conditional image captioning
    inputs = PROCESSOR(raw_image, text, return_tensors="pt").to("cuda", torch.float16)

    out = MODEL.generate(**inputs)
    output_text = PROCESSOR.decode(out[0], skip_special_tokens=True)
    return output_text


def infer(img, text: str = None):
    assert g_is_service_inited, f'❌️ blip-image-captioning-large 服务未初始化'
    raw_image = img.convert('RGB')
    text = g_sys_prompt if not text else text
    # conditional image captioning
    inputs = PROCESSOR(raw_image, text, return_tensors="pt").to("cuda", torch.float16)

    out = MODEL.generate(**inputs)
    output_text = PROCESSOR.decode(out[0], skip_special_tokens=True)
    return output_text
