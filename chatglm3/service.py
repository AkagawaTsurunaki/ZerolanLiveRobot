import json
import os
from typing import Final

import yaml
from loguru import logger

from chatglm3 import core
from common import is_port_in_use

DEFAULT_HOST: Final = "127.0.0.1"
DEFAULT_PORT: Final = 8721
DEFAULT_TOKENIZER_PATH: Final = 'THUDM/chatglm3-6b'
DEFAULT_MODEL_PATH: Final = 'THUDM/chatglm3-6b'
DEFAULT_QUANTIZE: Final = 4


def check_config():
    """
    检查配置文件是否无误
    :return:
    """
    # 读取配置文件

    logger.info('正在读取 ChatGLM3ServiceConfig……')
    with open('global_config.py', mode='r', encoding='utf-8') as file:
        config: dict = yaml.safe_load(file)

    # 检查 Port 是否可用

    port = config.get('port', DEFAULT_PORT)

    if is_port_in_use(port):
        logger.error(f"以下端口正在被占用：{port}")
        return

    host = config.get('host', DEFAULT_HOST)

    logger.info(f'LLM 服务地址：{host}:{port}')

    # 检查 Tokenizer 路径

    tokenizer_path = config.get('tokenizer_path', DEFAULT_TOKENIZER_PATH)
    if not os.path.exists(tokenizer_path):
        logger.error(f"Tokenizer 路径不存在：{tokenizer_path}")
        return
    logger.info(f'Tokenizer 路径：{tokenizer_path}')

    # 检查 Model 路径

    model_path = config.get('model_path', DEFAULT_MODEL_PATH)
    if not os.path.exists(model_path):
        logger.error(f"Model 路径不存在：{model_path}")
        return
    logger.info(f'Model 路径：{model_path}')

    # 检查量化级别

    quantize = config.get('quantize', DEFAULT_QUANTIZE)

    if quantize not in [4, 8]:
        logger.error(f'量化等级只能为 4 或 8，{quantize}不被支持')
        return

    logger.info("LLM 服务配置成功")


# def read_config(default_config_path: str):
#     try:
#         with open(file=default_config_path, mode='r', encoding='utf-8') as f:
#             config_dict = json.load(fp=f)
#             config = Config(**config_dict)
#             return config
#     except Exception as e:
#         logger.warning(e)
#         return None


# def arg_parse():
#     """
#     解析命令行参数
#     :return:
#     """
#     parser = argparse.ArgumentParser(description='LingController: LLM Web Service')
#     parser.add_argument('--debug', type=bool, default=False, help='是否以调试模式运行')
#     parser.add_argument('--host', type=str, help='LLM 服务的主机地址')
#     parser.add_argument('--port', type=int, help='LLM 服务的端口号')
#     parser.add_argument('--tokenizerpath', type=str, help='Tokenizer 的路径')
#     parser.add_argument('--modelpath', type=str, help='大语言模型的路径')
#     parser.add_argument('--quantize', type=int, help='量化等级')
#
#     args = parser.parse_args()
#     debug, host, port, tokenizer_path, model_path, quantize = (
#         args.debug, args.host, args.port, args.tokenizerpath, args.modelpath, args.quantize
#     )
#
#     return debug, host, port, tokenizer_path, model_path, quantize


# def handle_config():
    # 1. 先读取配置文件

    # config = read_config(default_config_path='./chatglm3/config.json')

    # 2. 如果命令行参数中，不为空的部分会覆盖配置文件中的值

    # debug, host, port, tokenizer_path, model_path, quantize = arg_parse()

    # 3. 将文件中的配置和命令行中的配置整理（命令行优先）

    # config.debug = debug if debug is not None else config.debug
    # config.host = host if host is not None else config.host
    # config.port = port if port is not None else config.port
    # config.tokenizer_path = tokenizer_path if tokenizer_path is not None else config.tokenizer_path
    # config.model_path = model_path if model_path is not None else config.model_path
    # config.quantize = quantize if quantize is not None else config.quantize

    # 4. 检查配置文件

    # check_config(config)
    #
    # return config


def predict(query: str, history: list, top_p: float, temperature: float, return_past_key_values: bool = True):
    return core.predict(query, history, top_p, temperature, return_past_key_values)
