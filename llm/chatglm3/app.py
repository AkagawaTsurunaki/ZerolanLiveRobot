from flask import Flask
from loguru import logger
from transformers import AutoTokenizer, AutoModel

from common.datacls import Chat, LLMQuery, LLMResponse
from common.exc import model_loading_log
from config import GLOBAL_CONFIG as G_CFG

_app = Flask(__name__)

_tokenizer: any
_model: any


@model_loading_log
def init():
    global _model, _tokenizer

    llm_cfg = G_CFG.large_language_model
    model_path, quantize = llm_cfg.models[0].model_path, llm_cfg.models[0].quantize

    _tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    if quantize:
        _model = AutoModel.from_pretrained(model_path, trust_remote_code=True).quantize(quantize).to(
            'cuda').eval()
    else:
        _model = AutoModel.from_pretrained(model_path, trust_remote_code=True).to('cuda').eval()
    assert _tokenizer and _model


def _to_chatglm_format(llm_query: LLMQuery) -> (str, list[dict[str:str]]):
    text = llm_query.text
    history = [{'role': chat.role, 'metadata': '', 'content': chat.content} for chat in llm_query.history]
    return text, history


def _to_pipeline_format(response: str, history: list[dict[str:str]]) -> LLMResponse:
    history = [Chat(role=chat['role'], content=chat['content']) for chat in history]
    llm_response = LLMResponse(response=response, history=history)
    return llm_response


def predict(llm_query: LLMQuery) -> LLMResponse:
    """
    ChatGLM 推理
    :param llm_query:
    :return:
    """
    text, history = _to_chatglm_format(llm_query)
    response, history = _model.chat(_tokenizer, text, history, top_p=1., temperature=1., past_key_values=None)
    logger.debug(response)
    return _to_pipeline_format(response, history)


def stream_predict(llm_query: LLMQuery):
    """
    ChatGLM 流式推理
    :param llm_query:
    :return:
    """
    text, history = _to_chatglm_format(llm_query)
    for response, history, past_key_values in _model.stream_chat(_tokenizer, text, history=history, top_p=1.,
                                                                 temperature=1.,
                                                                 past_key_values=None,
                                                                 return_past_key_values=True):
        logger.debug(response)
        yield _to_pipeline_format(response, history)
