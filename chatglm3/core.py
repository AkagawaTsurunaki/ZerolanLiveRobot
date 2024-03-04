import torch
from loguru import logger
from transformers import AutoTokenizer, AutoModel

tokenizer, model = None, None


def init(tokenizer_path: str, model_path: str, quantize: int):
    """
    初始化服务核心
    Note: 请在使用此模块前先调用此函数
    """
    global tokenizer, model

    # 检查 CUDA 是否可用

    if torch.cuda.is_available():
        device = 'cuda'
        logger.info('CUDA 设备可用')
    else:
        device = 'cpu'
        logger.warning('CUDA 设备不可用，使用 CPU 进行推理可能效果十分不理想')

    # 加载 Tokenizer

    logger.info('Tokenizer 正在加载……')
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, trust_remote_code=True)
    if tokenizer is not None:
        logger.info('Tokenizer 加载成功')
    else:
        logger.critical('Tokenizer 加载失败')
        return

    # 加载 LLM

    logger.info('LLM 正在加载……')
    model = AutoModel.from_pretrained(model_path, trust_remote_code=True).quantize(quantize).cuda().to(
        device).eval()
    logger.info(f'LLM 以 {quantize}-bit 加载成功')


def predict(query: str, history: list, top_p: int, temperature: float, return_past_key_values: bool) -> (str, list):
    global tokenizer, model
    assert tokenizer is not None and model is not None

    ret_response = ''
    ret_history = None
    past_key_values = None

    for response, history, past_key_values in model.stream_chat(tokenizer,
                                                                query,
                                                                history=history,
                                                                top_p=top_p,
                                                                temperature=temperature,
                                                                past_key_values=past_key_values,
                                                                return_past_key_values=return_past_key_values):
        ret_response = response
        ret_history = history

    logger.info(f'来自 ChatGLM 的消息：{ret_response}')
    return ret_response, ret_history
