import os

from flask import Flask
from loguru import logger
from transformers import AutoModelForCausalLM, AutoTokenizer

from common.datacls import ModelNameConst as MNC, Chat, LLMQuery, LLMResponse, Role
from common.exc import model_loading_log
from config import GLOBAL_CONFIG as G_CFG

# 指定使用哪张显卡
logger.warning(f'⚠️ 模型 {MNC.QWEN} 并不支持多卡推理，因此默认使用第 1 显卡。')
os.environ['CUDA_VISIBLE_DEVICES'] = '0'

_app = Flask(__name__)

_host: str
_port: int
_debug: bool

_tokenizer: any
_model: any


@model_loading_log
def init():
    global _model, _tokenizer, _host, _port, _debug, _streamer

    llm_cfg = G_CFG.large_language_model
    mode, model_path = llm_cfg.models[0].loading_mode, llm_cfg.models[0].model_path

    if mode == 'bf16':
        _model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto", trust_remote_code=True,
                                                      bf16=True).eval()
    elif mode == 'fp16':
        _model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto", trust_remote_code=True,
                                                      fp16=True).eval()
    elif mode == 'cpu':
        _model = AutoModelForCausalLM.from_pretrained(model_path, device_map="cpu", trust_remote_code=True).eval()
    else:
        _model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto", trust_remote_code=True).eval()

    _tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    assert _tokenizer and _model


def to_qwen_format(llm_query: LLMQuery) -> (str, list[tuple[str, str]], str):
    history_content_list: list[str] = [chat.content for chat in llm_query.history]

    sys_prompt = None
    # Concat system prompt with the first conversation content
    if llm_query.history[0].role == Role.SYSTEM:
        sys_prompt = llm_query.history[0].content
        if len(history_content_list) > 0:
            history_content_list = history_content_list[1:]
            history_content_list[0] = sys_prompt + history_content_list[0]

    assert len(history_content_list) % 2 == 0, f'Length of the history for Qwen must be even number.'

    # Convert content list as tuple
    history: list[tuple] = []

    for i in range(0, len(history_content_list), 2):
        history.append((history_content_list[i], history_content_list[i + 1]))

    text = llm_query.text
    return text, history, sys_prompt


def to_pipeline_format(response: str, history: list[tuple[str, str]], sys_prompt: str) -> LLMResponse:
    # 将 history 转化为 pipeline 的格式
    ret_history: list[Chat] = []
    for chat in history:
        q, r = chat[0], chat[1]
        assert isinstance(q, str) and isinstance(r, str)
        ret_history.append(Chat(role=Role.USER, content=q))
        ret_history.append(Chat(role=Role.ASSISTANT, content=r))

    # 获取系统提示词
    if sys_prompt:
        ret_history[0].content = ret_history[0].content[len(sys_prompt):]
        ret_history.insert(0, Chat(role=Role.SYSTEM, content=sys_prompt))

    llm_response = LLMResponse(response=response, history=ret_history)

    return llm_response


def predict(llm_query: LLMQuery):
    """
    Qwen-7B-Chat 推理
    :param llm_query:
    :return:
    """
    text, history, sys_prompt = to_qwen_format(llm_query)
    response, history = _model.chat(_tokenizer, llm_query.text, history=history)
    logger.debug(response)
    return to_pipeline_format(response, history, sys_prompt)


def stream_predict(llm_query: LLMQuery):
    """
    Qwen-7B-Chat 流式推理
    :param llm_query:
    :return:
    """
    text, history, sys_prompt = to_qwen_format(llm_query)
    for response in _model.chat_stream(_tokenizer, llm_query.text, history=history):
        logger.debug(response)
        yield to_pipeline_format(response, history, sys_prompt)
