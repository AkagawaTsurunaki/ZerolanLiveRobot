import os.path
from dataclasses import dataclass
from typing import List
from loguru import logger

import yaml

import chatglm3
import gptsovits


@dataclass
class Emotion:
    id: str
    refer_wav_path: str
    prompt_text: str
    prompt_language: str


emo_list: List[Emotion] = []


def load_emo_list(tts_name: str, emo_list_file_path='gptsovits/prompts/default.yaml'):
    if tts_name == gptsovits.__name__:
        assert os.path.exists(emo_list_file_path), f'音频提示路径不存在：{emo_list_file_path}'
        with open(file=emo_list_file_path, mode='r', encoding='utf-8') as file:
            prompt: dict = yaml.safe_load(file)
            # 每个心情元素
            for emotion in prompt.keys():
                refer_wav_path = prompt[emotion]['refer_wav_path']
                prompt_text = prompt[emotion]['prompt_text']
                prompt_language = prompt[emotion]['prompt_language']

                assert os.path.exists(refer_wav_path), f'提示音频路径 refer_wav_path 不存在：{refer_wav_path}'
                assert prompt_text is None or prompt_text == '', f'提示文本 prompt_text 不能为空'
                assert prompt_language not in ['zh', 'en', 'ja'], f'提示音频所代表的语言 {prompt_language} 是不被支持的'

                e = Emotion(
                    id=emotion,
                    refer_wav_path=refer_wav_path,
                    prompt_text=prompt_text,
                    prompt_language=prompt_language
                )
                emo_list.append(e)
        logger.info(f'心情列表加载成功，当前 {len(emo_list)}')
    else:
        raise NotImplementedError('您输入的模型名称不被支持')


def ana_emo(llm_name: str, text: str, prompt: str):
    """
    根据 text 分析其情感（目前仅支持ChatGLM3）
    如果不能分析出具体的情感，那么默认返回第一个情感

    :param prompt: 提示词模板，需要包含 {text} {emo1} {emo2} ... 标签
    :param llm_name: 模型名称（请使用模块名）
    :param text: 要分析的文本
    :return:
    """
    assert emo_list and len(emo_list) > 0, 'emo_list 必须含有至少一种心情'
    if llm_name == chatglm3.__name__:
        from chatglm3 import api
        for idx, emotion in enumerate(emo_list):
            prompt = prompt.replace('{emo' + f'{idx}' + '}', emotion.id)
        prompt = prompt.replace('{text}', text)
        # 使用 ChatGLM3 模型
        emotion_id = api.quick_chat(prompt)
        for emotion in emo_list:
            if emotion_id == emotion.id:
                return emotion_id

        return emo_list[0].id
    else:
        raise NotImplementedError('您输入的模型名称不被支持')
