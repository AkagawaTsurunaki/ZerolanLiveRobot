from loguru import logger


def predict(query: str, history: list = None, top_p: float = 1., temperature: float = 1.,
            return_past_key_values: bool = True) -> (str, list):
    from . import TOKENIZER, MODEL
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
