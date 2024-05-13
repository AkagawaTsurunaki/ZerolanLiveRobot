from flask import Flask
from transformers import AutoModelForCausalLM, AutoTokenizer

from common.datacls import Chat, LLMResponse, Role, LLMQuery
from common.exc import llm_loading_log
from config import GLOBAL_CONFIG as G_CFG

_app = Flask(__name__)

_tokenizer: any
_model: any


@llm_loading_log
def init():
    global _model, _tokenizer

    llm_cfg = G_CFG.large_language_model
    _host, _port, _debug = llm_cfg.host, llm_cfg.port, llm_cfg.debug
    model_path, mode = llm_cfg.models[0].model_path, llm_cfg.models[0].loading_mode

    _tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=False)
    _model = AutoModelForCausalLM.from_pretrained(
        model_path,
        device_map=mode,
    ).eval()
    assert _tokenizer and _model


def _to_yi_format(llm_query: LLMQuery):
    messages = [{"role": chat.role, "content": chat.content} for chat in llm_query.history]
    messages.append({"role": Role.USER, "content": llm_query.text})
    return messages


def _to_pipeline_format(response, messages):
    messages.append({"role": Role.ASSISTANT, "content": response})
    history = [Chat(role=chat['role'], content=chat['content']) for chat in messages]
    return LLMResponse(response, history)


def predict(llm_query):
    """
    Yi-6B 推理
    :param llm_query:
    :return:
    """
    messages = _to_yi_format(llm_query)
    input_ids = _tokenizer.apply_chat_template(conversation=messages, tokenize=True,
                                               add_generation_prompt=True,
                                               return_tensors='pt').to('cuda')
    output_ids = _model.generate(input_ids)
    response = _tokenizer.decode(output_ids[0][input_ids.shape[1]:], skip_special_tokens=True)

    return _to_pipeline_format(response, messages)


def stream_predict(llm_query: LLMQuery):
    raise NotImplementedError('Yi-6B 暂时不支持流式推理')
