import os

import torch
import yaml
from loguru import logger
from transformers import AutoTokenizer, AutoModel

from common import is_port_in_use


class ChatGLM3Service:

    def __init__(self):
        self.HOST = "127.0.0.1"
        self.PORT = 8721
        self.TOKENIZER_PATH = 'THUDM/chatglm3-6b'
        self.MODEL_PATH = 'THUDM/chatglm3-6b'
        self.QUANTIZE = 4
        self.TOKENIZER = None
        self.MODEL = None

        # 初始化
        config = self.load_config()
        self.init_service(config)

    def load_config(self):
        """
        检查配置文件是否无误
        :return: 配置字典
        """
        # 读取配置文件

        logger.info('正在读取 ChatGLM3ServiceConfig……')

        if not os.path.exists('global_config.yaml'):
            logger.error('全局配置文件缺失，请在项目根目录下新建 global_config.yaml 进行配置')
            return

        with open('global_config.yaml', mode='r', encoding='utf-8') as file:
            config: dict = yaml.safe_load(file)
            config = config.get('ChatGLM3ServiceConfig', None)

        if not config:
            logger.error('无法读取 ChatGLM3ServiceConfig，格式不正确')

        # 检查 Port 是否可用

        port = config.get('port', self.PORT)

        if is_port_in_use(port):
            logger.error(f"以下端口正在被占用：{port}")
            return

        host = config.get('host', self.HOST)

        logger.info(f'LLM 服务地址：{host}:{port}')

        # 检查 Tokenizer 路径

        tokenizer_path = config.get('tokenizer_path', self.TOKENIZER_PATH)
        if not os.path.exists(tokenizer_path):
            logger.error(f"Tokenizer 路径不存在：{tokenizer_path}")
            return
        logger.info(f'Tokenizer 路径：{tokenizer_path}')

        # 检查 Model 路径

        model_path = config.get('model_path', self.MODEL_PATH)
        if not os.path.exists(model_path):
            logger.error(f"Model 路径不存在：{model_path}")
            return
        logger.info(f'Model 路径：{model_path}')

        # 检查量化级别

        quantize = config.get('quantize', self.QUANTIZE)

        if quantize not in [4, 8]:
            logger.error(f'量化等级只能为 4 或 8，{quantize}不被支持')
            return

        logger.info("LLM 服务配置成功")

        return config

    def init_service(self, config: dict):
        """
        初始化服务核心
        """

        # 解出配置信息

        tokenizer_path = config.get('tokenizer_path', self.TOKENIZER_PATH)
        model_path = config.get('model_path', self.MODEL_PATH)
        quantize = config.get('quantize', self.QUANTIZE)

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

    def predict(self, query: str, history: list = None, top_p: float = 1., temperature: float = 1.,
                return_past_key_values: bool = True) -> (str, list):
        ret_response = ''
        ret_history = None
        past_key_values = None

        for response, history, past_key_values in MODEL.stream_chat(TOKENIZER,
                                                                    query,
                                                                    history=history if history else [],
                                                                    top_p=top_p,
                                                                    temperature=temperature,
                                                                    past_key_values=past_key_values,
                                                                    return_past_key_values=return_past_key_values):
            ret_response = response
            ret_history = history

        logger.info(f'来自 ChatGLM3 的消息：{ret_response}')
        return ret_response, ret_history

    def stream_predict(self, query: str, history: list = None, top_p: float = 1., temperature: float = 1.,
                       return_past_key_values: bool = True) -> (str, list):
        past_key_values = None

        yield MODEL.stream_chat(TOKENIZER,
                                query,
                                history=history if history else [],
                                top_p=top_p,
                                temperature=temperature,
                                past_key_values=past_key_values,
                                return_past_key_values=return_past_key_values)
