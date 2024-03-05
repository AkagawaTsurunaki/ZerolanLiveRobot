import os
from typing import Final

import torch
import yaml
from loguru import logger
from transformers import AutoTokenizer, AutoModel

from chatglm3 import service
from common import is_port_in_use

HOST = "127.0.0.1"
PORT = 8721
TOKENIZER_PATH = 'THUDM/chatglm3-6b'
MODEL_PATH = 'THUDM/chatglm3-6b'
QUANTIZE = 4

TOKENIZER = None
MODEL = None


def load_config():
    """
    检查配置文件是否无误
    :return: 配置字典
    """
    # 读取配置文件

    logger.info('正在读取 ChatGLM3ServiceConfig……')
    with open('global_config.py', mode='r', encoding='utf-8') as file:
        config: dict = yaml.safe_load(file)

    # 检查 Port 是否可用

    port = config.get('port', PORT)

    if is_port_in_use(port):
        logger.error(f"以下端口正在被占用：{port}")
        return

    host = config.get('host', HOST)

    logger.info(f'LLM 服务地址：{host}:{port}')

    # 检查 Tokenizer 路径

    tokenizer_path = config.get('tokenizer_path', TOKENIZER_PATH)
    if not os.path.exists(tokenizer_path):
        logger.error(f"Tokenizer 路径不存在：{tokenizer_path}")
        return
    logger.info(f'Tokenizer 路径：{tokenizer_path}')

    # 检查 Model 路径

    model_path = config.get('model_path', MODEL_PATH)
    if not os.path.exists(model_path):
        logger.error(f"Model 路径不存在：{model_path}")
        return
    logger.info(f'Model 路径：{model_path}')

    # 检查量化级别

    quantize = config.get('quantize', QUANTIZE)

    if quantize not in [4, 8]:
        logger.error(f'量化等级只能为 4 或 8，{quantize}不被支持')
        return

    logger.info("LLM 服务配置成功")

    return config


def init_service(config: dict):
    """
    初始化服务核心
    """

    # 解出配置信息

    tokenizer_path = config.get('tokenizer_path', TOKENIZER_PATH)
    model_path = config.get('model_path', MODEL_PATH)
    quantize = config.get('quantize', QUANTIZE)

    # 检查 CUDA 是否可用

    if torch.cuda.is_available():
        device = 'cuda'
        logger.info('CUDA 设备可用')
    else:
        device = 'cpu'
        logger.warning('CUDA 设备不可用，使用 CPU 进行推理可能效果十分不理想')

    # 加载 Tokenizer

    global TOKENIZER
    logger.info('Tokenizer 正在加载……')
    TOKENIZER = AutoTokenizer.from_pretrained(tokenizer_path, trust_remote_code=True)
    if TOKENIZER is not None:
        logger.info('Tokenizer 加载成功')
    else:
        logger.critical('Tokenizer 加载失败')
        return

    # 加载 LLM

    global MODEL
    logger.info('LLM 正在加载……')
    MODEL = AutoModel.from_pretrained(model_path, trust_remote_code=True).quantize(quantize).cuda().to(
        device).eval()
    logger.info(f'LLM 以 {quantize}-bit 加载成功')


config = load_config()
init_service(config)
