import copy
import sys
from typing import List

from loguru import logger

from config import GlobalConfig
from llm.pipeline import LLMPipeline
from utils import util
from utils.datacls import Tone, LLMQuery, Chat, Role

logger.remove()
handler_id = logger.add(sys.stderr, level="INFO")


class ToneAnalysisService:
    def __init__(self, cfg: GlobalConfig):
        # All tone loaded and stored here. Once it inited, it should not be changed anymore.
        self._tone_list: list[Tone] = []
        # LLM Pipeline, for analyse a sentence's tone.
        self._llm_pipeline: LLMPipeline = LLMPipeline(cfg)
        # LLM query for analysing tone of a sentence. Should only change the text attribute.
        self._tone_analysis_template: LLMQuery

        tone_analysis_template_path = cfg.tone_analysis.tone_analysis_template_path
        tone_analysis_template_dict = util.read_yaml(tone_analysis_template_path)
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
            self._tone_list.append(tone)
            examples: list[str] = tone_dict[tone_id].get('examples', None)
            assert examples, f'Can not find any example for tone analysis service, please check your template file "{tone_analysis_template_path}".'
            for example in examples:
                history += [Chat(role=Role.USER, content=f'{task}\n{example}')]
                history += [Chat(role=Role.ASSISTANT, content=tone_id)]
        self._tone_analysis_template = LLMQuery('', history)

    def analyze_tone(self, text: str) -> Tone:
        """
        Analyze the sentiment of the given text.
        If it cannot determine a specific sentiment, return the first sentiment by default.

        :param text: The text to be analyzed
        :return:
        """
        # Query for LLM to get tone_id
        llm_query = copy.deepcopy(self._tone_analysis_template)
        llm_query.text = text
        llm_response = self._llm_pipeline.predict(query=llm_query)
        tone_id = llm_response.response

        # Check if valid tone_list
        for tone in self._tone_list:
            if tone.id == tone_id:
                return tone
        return self._tone_list[0]
