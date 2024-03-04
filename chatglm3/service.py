import argparse
import json
import os

from loguru import logger

from common import is_port_in_use, HttpResponseBody, Code
from chatglm3.common import Config


def check_config(config: Config):
    """
    检查配置文件是否无误
    :param config:
    :return:
    """

    logger.info('正在检查配置')

    # 1. 检查 Port 是否被占用

    assert config.port is not None
    if is_port_in_use(config.port):
        logger.error(f"以下端口正在被占用：{config.port}")
        return HttpResponseBody(
            code=Code.PORT_IS_ALREADY_USED.value,
            msg=f"以下端口正在被占用：{config.port}",
        )
    logger.info(f'LLM 服务地址：{config.host}:{config.port}')

    # 2. 检查 Tokenizer 路径

    assert config.tokenizer_path is not None
    if not os.path.exists(config.tokenizer_path):
        logger.error(f"Tokenizer 路径不存在：{config.tokenizer_path}")
        return HttpResponseBody(
            code=Code.PATH_DOSE_NOT_EXIST.value,
            msg=f"Tokenizer 路径不存在：{config.tokenizer_path}",
        )
    logger.info(f'Tokenizer 路径：{config.tokenizer_path}')

    # 3. 检查 Model 路径

    assert config.model_path is not None
    if not os.path.exists(config.model_path):
        logger.error(f"Model 路径不存在：{config.model_path}")
        return HttpResponseBody(
            code=Code.PATH_DOSE_NOT_EXIST.value,
            msg=f"Model 路径不存在：{config.model_path}",
        )
    logger.info(f'Model 路径：{config.model_path}')

    # 4. 检查量化级别

    assert config.quantize is not None
    if config.quantize not in [4, 8]:
        logger.error(f'量化等级只能为 4 或 8，{config.quantize}不被支持。')
        return

    logger.info("LLM 服务配置成功")
    return HttpResponseBody(
        code=Code.OK.value,
        msg="LLM 服务配置成功"
    )


def read_config(default_config_path: str):
    try:
        with open(file=default_config_path, mode='r', encoding='utf-8') as f:
            config_dict = json.load(fp=f)
            config = Config(**config_dict)
            return config
    except Exception:
        return None


def arg_parse():
    """
    解析命令行参数
    :return:
    """
    parser = argparse.ArgumentParser(description='LingController: LLM Web Service')
    parser.add_argument('--debug', type=bool, default=False, help='是否以调试模式运行')
    parser.add_argument('--host', type=str, help='LLM 服务的主机地址')
    parser.add_argument('--port', type=int, help='LLM 服务的端口号')
    parser.add_argument('--tokenizerpath', type=str, help='Tokenizer 的路径')
    parser.add_argument('--modelpath', type=str, help='大语言模型的路径')
    parser.add_argument('--quantize', type=int, help='量化等级')

    args = parser.parse_args()
    debug, host, port, tokenizer_path, model_path, quantize = (
        args.debug, args.host, args.port, args.tokenizerpath, args.modelpath, args.quantize
    )

    return debug, host, port, tokenizer_path, model_path, quantize


def handle_config():
    # 1. 先读取配置文件

    config = read_config(default_config_path='./chatglm3/config.json')

    # 2. 如果命令行参数中，不为空的部分会覆盖配置文件中的值

    debug, host, port, tokenizer_path, model_path, quantize = arg_parse()

    # 3. 将文件中的配置和命令行中的配置整理（命令行优先）

    config.debug = debug if debug is not None else config.debug
    config.host = host if host is not None else config.host
    config.port = port if port is not None else config.port
    config.tokenizer_path = tokenizer_path if tokenizer_path is not None else config.tokenizer_path
    config.model_path = model_path if model_path is not None else config.model_path
    config.quantize = quantize if quantize is not None else config.quantize

    # 4. 检查配置文件

    check_config(config)

    return config
