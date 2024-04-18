import copy
import sys
from typing import List

from loguru import logger

import initzr
from llm.pipeline import LLMPipeline
from utils import util
from utils.datacls import Chat, Role, NewLLMQuery
from utils.datacls import Tone

logger.remove()
handler_id = logger.add(sys.stderr, level="INFO")

# Configuration for tone analysis service
CONFIG = initzr.load_tone_analysis_service_config()

# All tone loaded and stored here. Once it inited, it should not be changed anymore.
tone_list: list[Tone] = []

# LLM Pipeline, for analyse a sentence's tone.
LLM_PIPELINE: LLMPipeline = LLMPipeline()

# LLM query for analysing tone of a sentence. Should only change the text attribute.
tone_analysis_template: NewLLMQuery


def _init():
    global tone_analysis_template, LLM_PIPELINE
    tone_analysis_template_dict = util.read_yaml(CONFIG.tone_analysis_template_path)
    task: str = tone_analysis_template_dict['task']
    tone_dict: dict = tone_analysis_template_dict['tone']
    history: List[Chat] = []
    for tone_id in tone_dict.keys():
        tone = Tone(
            id=tone_id,
            refer_wav_path=tone_dict[tone_id]['refer_wav_path'],
            prompt_text=tone_dict[tone_id]['prompt_text'],
            prompt_language=tone_dict[tone_id]['prompt_language']
        )
        tone_list.append(tone)
        examples: list[str] = tone_dict[tone_id].get('examples', None)
        assert examples, f'Can not find any example for tone analysis service, please check your template file "{CONFIG.tone_analysis_template_path}".'
        for example in examples:
            history += [Chat(role=Role.USER, content=f'{task}\n{example}')]
            history += [Chat(role=Role.ASSISTANT, content=tone_id)]
    tone_analysis_template = NewLLMQuery('', history)


def analyze_tone(text: str) -> Tone:
    """
    根据 text 分析其情感（目前仅支持ChatGLM3）
    如果不能分析出具体的情感，那么默认返回第一个情感

    :param text: 要分析的文本
    :return:
    """
    # Query for LLM to get tone_id
    llm_query = copy.deepcopy(tone_analysis_template)
    llm_query.text = text
    llm_response = LLM_PIPELINE.predict(llm_query=llm_query)
    tone_id = llm_response.response

    # Check if valid tone_list
    for tone in tone_list:
        if tone.id == tone_id:
            return tone
    return tone_list[0]


_init()
