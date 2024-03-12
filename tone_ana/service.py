import json
import os
import random
import sys
from dataclasses import dataclass
from os import PathLike
from typing import List

import yaml
from loguru import logger

import chatglm3.api
from chatglm3.service import LLMQuery

logger.remove()
handler_id = logger.add(sys.stderr, level="INFO")


@dataclass
class Tone:
    id: str
    refer_wav_path: str
    prompt_text: str
    prompt_language: str


tone_list: List[Tone] = []

# 加载给 LLM 的模板，用于分析语气
g_llm_query: LLMQuery
TONE_TEMPLATE_PATH: str = 'template/tone_list.yaml'
PROMPT_FOR_LLM_PATH: str = ''


def load_tone_list():
    # 加载语气模板列表
    with open(file=TONE_TEMPLATE_PATH, mode='r', encoding='utf-8') as file:
        prompt: dict = yaml.safe_load(file)
        # 每个心情元素
        for emotion in prompt.keys():
            refer_wav_path = prompt[emotion]['refer_wav_path']
            prompt_text = prompt[emotion]['prompt_text']
            prompt_language = prompt[emotion]['prompt_language']

            assert os.path.exists(refer_wav_path), f'❌️ 提示音频路径 refer_wav_path 不存在：{refer_wav_path}'
            assert not (prompt_text is None or prompt_text == ''), f'❌️ 提示文本 prompt_text 不能为空'
            assert prompt_language in ['zh', 'en', 'ja'], f'❌️ 提示音频所代表的语言 {prompt_language} 是不被支持的'

            tone = Tone(
                id=emotion,
                refer_wav_path=refer_wav_path,
                prompt_text=prompt_text,
                prompt_language=prompt_language
            )
            tone_list.append(tone)
    assert len(tone_list) > 0, '❌️ 必须含有至少一种心情'


def load_llm_ana_prompt():
    # 加载给 LLM 的模板，用于分析语气
    global g_llm_query
    with open(file=PROMPT_FOR_LLM_PATH, mode='r', encoding='utf-8') as file:
        g_llm_query = LLMQuery(**json.load(file))
        tone_list_rep = ''
        for idx, tone in enumerate(tone_list):
            tone_list_rep += f'{tone.id},'
            g_llm_query.history[2 * idx + 1]['content'] = g_llm_query.history[2 * idx + 1]['content'].replace(
                '{tone_id}',
                tone.id)

        g_llm_query.history[0]['content'] = g_llm_query.history[0]['content'].replace('tone_list', tone_list_rep)


def init(tone_template_path: str | PathLike, prompt_for_llm_path: str | PathLike):
    global tone_list, TONE_TEMPLATE_PATH, PROMPT_FOR_LLM_PATH

    logger.info('💖 语气分析服务初始化中……')
    TONE_TEMPLATE_PATH = tone_template_path
    PROMPT_FOR_LLM_PATH = prompt_for_llm_path

    load_tone_list()
    logger.info(f'💖 语气列表加载成功，当前 {len(tone_list)}')

    load_llm_ana_prompt()
    logger.info('💖 语气分析服务初始化完毕')

    return True


def analyze_tone(text: str):
    """
    根据 text 分析其情感（目前仅支持ChatGLM3）
    如果不能分析出具体的情感，那么默认返回第一个情感

    :param text: 要分析的文本
    :return:
    """

    # 模板提示替换关键词
    g_llm_query.query = g_llm_query.query.replace('{text}', text)

    # 向 ChatGLM3 查询心情 ID
    emotion_id, _ = chatglm3.api.predict(query=g_llm_query.query, history=g_llm_query.history)

    # 校验心情 ID 是否合法
    for tone in tone_list:
        if emotion_id == tone.id:
            return tone

    # 不合法随机返回一个
    return random.sample(tone_list, 1)[0]
