import copy
import sys

from loguru import logger

import zio.util
from common.datacls import Tone, Chat, LLMQuery, Role
from config import GlobalConfig
from llm.pipeline import LLMPipeline

logger.remove()
handler_id = logger.add(sys.stderr, level="INFO")

# All tone loaded and stored here. Once it inited, it should not be changed anymore.
_tone_list: list[Tone]
# LLM Pipeline, for analyse a sentence's tone.
_llm_pipeline: LLMPipeline
# LLM query for analysing tone of a sentence. Should only change the text attribute.
_tone_analysis_template: LLMQuery


def init(cfg: GlobalConfig):
    global _tone_list, _llm_pipeline, _tone_analysis_template

    _tone_list = []
    _llm_pipeline = LLMPipeline(cfg)

    tone_analysis_template_path = cfg.tone_analysis.tone_analysis_template_path
    tone_analysis_template_dict = zio.util.read_yaml(tone_analysis_template_path)
    task = tone_analysis_template_dict['task']
    tone_dict = tone_analysis_template_dict['tone']
    history = []
    for tone_id in tone_dict.keys():
        tone = Tone(
            id=tone_id,
            refer_wav_path=tone_dict[tone_id]['refer_wav_path'],
            prompt_text=tone_dict[tone_id]['prompt_text'],
            prompt_language=tone_dict[tone_id]['prompt_language']
        )
        _tone_list.append(tone)
        examples: list[str] = tone_dict[tone_id].get('examples', None)
        assert examples, f'Can not find any example for tone analysis service, please check your template file "{tone_analysis_template_path}".'
        for example in examples:
            history += [Chat(role=Role.USER, content=f'{task}\n{example}')]
            history += [Chat(role=Role.ASSISTANT, content=tone_id)]
    _tone_analysis_template = LLMQuery('', history)


def analyze_tone(text: str) -> Tone:
    """
    Analyze the sentiment of the given text.
    If it cannot determine a specific sentiment, return the first sentiment by default.

    :param text: The text to be analyzed
    :return:
    """
    # Query for LLM to get tone_id
    llm_query = copy.deepcopy(_tone_analysis_template)
    llm_query.text = text
    llm_response = _llm_pipeline.predict(query=llm_query)
    tone_id = llm_response.response

    # Check if valid tone_list
    for tone in _tone_list:
        if tone.id == tone_id:
            return tone
    return _tone_list[0]
