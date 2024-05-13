"""
More detail, please see:
https://huggingface.co/augmxnt/shisa-7b-v1
"""
import copy

import torch
from flask import Flask
from transformers import AutoTokenizer, AutoModelForCausalLM, TextStreamer

from common.datacls import Chat, LLMQuery, LLMResponse, Role
from common.exc import model_loading_log
from config import GLOBAL_CONFIG as G_CFG

_app = Flask(__name__)

_tokenizer: any
_model: any
_streamer: TextStreamer


@model_loading_log
def init():
    global _tokenizer, _model, _streamer

    llm_cfg = G_CFG.large_language_model
    model_path = llm_cfg.models[0].model_path

    _tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=True)
    _model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16,
    ).to('cuda')
    _streamer = TextStreamer(_tokenizer, skip_prompt=True)
    assert _tokenizer and _model and _streamer


def _to_shisa_format(llm_query: LLMQuery):
    assert len(llm_query.history) > 0 and llm_query.history[0].role == Role.SYSTEM, f'システムプロンプトは必要です。'

    llm_query_history = copy.deepcopy(llm_query.history)
    llm_query_history.append(Chat(role=Role.USER, content=llm_query.text))
    history = [{"role": chat.role, "content": chat.content} for chat in llm_query_history]
    return history


def _to_pipeline_format(response, history):
    history.append(Chat(role=Role.ASSISTANT, content=response))
    return LLMResponse(response=response, history=history)


def predict(llm_query: LLMQuery):
    """
    Shisa 推理
    :param llm_query:
    :return:
    """
    history = _to_shisa_format(llm_query)

    inputs = _tokenizer.apply_chat_template(history, add_generation_prompt=True, return_tensors="pt")
    first_param_device = next(_model.parameters()).device
    inputs = inputs.to(first_param_device)

    with torch.no_grad():
        outputs = _model.generate(
            inputs,
            pad_token_id=_tokenizer.eos_token_id,
            max_new_tokens=500,
            temperature=0.5,
            repetition_penalty=1.15,
            top_p=0.95,
            do_sample=True,
            streamer=_streamer,
        )

    new_tokens = outputs[0, inputs.size(1):]
    response = _tokenizer.decode(new_tokens, skip_special_tokens=True)

    return _to_pipeline_format(response, llm_query.history)


def stream_predict(llm_query: LLMQuery):
    raise NotImplementedError('ストリーム生成の方法はまだインプリメントしません。')
