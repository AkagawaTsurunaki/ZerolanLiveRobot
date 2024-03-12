import psutil
from loguru import logger
from transformers import AutoTokenizer, AutoModel

TOKENIZER: AutoTokenizer
MODEL: AutoModel
IS_INITIALIZED = False
MODEL_PROMPT = None


def init(tokenizer_path, model_path, quantize):
    global TOKENIZER, MODEL, IS_INITIALIZED, MODEL_PROMPT
    TOKENIZER = AutoTokenizer.from_pretrained(tokenizer_path, trust_remote_code=True)
    MODEL = AutoModel.from_pretrained(model_path, trust_remote_code=True).quantize(quantize).to('cuda').eval()
    logger.info(f'💭 ChatGLM3 以 {quantize}-bit 加载完毕')
    IS_INITIALIZED = True
    return IS_INITIALIZED


def is_port_in_use(port):
    """
    检查指定端口是否被占用
    :param port: int, 待检查的端口号
    :return: bool, 如果端口被占用返回 True，否则返回 False
    """
    for proc in psutil.process_iter():
        for con in proc.connections():
            if con.status == 'LISTEN' and con.laddr.port == port:
                return True
    return False


def predict(query: str, history: list = None, top_p: float = 1., temperature: float = 1.,
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

    return ret_response, ret_history


def stream_predict(query: str, history: list = None, top_p: float = 1., temperature: float = 1.,
                   return_past_key_values: bool = True):
    past_key_values = None

    yield MODEL.stream_chat(TOKENIZER,
                            query,
                            history=history if history else [],
                            top_p=top_p,
                            temperature=temperature,
                            past_key_values=past_key_values,
                            return_past_key_values=return_past_key_values)


