from loguru import logger

from chatglm3 import TOKENIZER, MODEL


def predict(query: str, history: list, top_p: float, temperature: float, return_past_key_values: bool) -> (str, list):
    ret_response = ''
    ret_history = None
    past_key_values = None

    for response, history, past_key_values in MODEL.stream_chat(TOKENIZER,
                                                                query,
                                                                history=history,
                                                                top_p=top_p,
                                                                temperature=temperature,
                                                                past_key_values=past_key_values,
                                                                return_past_key_values=return_past_key_values):
        ret_response = response
        ret_history = history

    logger.info(f'来自 ChatGLM3 的消息：{ret_response}')
    return ret_response, ret_history
