import json
import os
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Tuple

from loguru import logger

from common.enum.lang import Language
from common.utils.file_util import read_yaml, spath
from services.llm.pipeline import Conversation


@dataclass
class TTSPrompt:
    audio_path: str
    lang: Language
    sentiment: str
    transcript: str


class CharacterConfig(ABC):
    def __init__(self):
        self.config_dict: dict = {}
        self.system_prompt: str = ""
        self.example_cases: List[Conversation] = []
        self.tts_prompts: List[TTSPrompt] = []

    @abstractmethod
    def load_config(self):
        self.load_llm_prompts()
        self.load_tts_prompts()
        logger.info("角色配置加载完成")

    @abstractmethod
    def load_llm_prompts(self):
        pass

    @abstractmethod
    def load_tts_prompts(self):
        pass


class CustomCharacterConfig(CharacterConfig):
    """
    这是一个样例，可以自己实现。
    """

    def __init__(self):
        super().__init__()
        self.user_input_format: dict = {}

    def load_config(self):
        super().load_config()

    def load_llm_prompts(self):

        config_dict = read_yaml(spath("resources/config/character_config.yaml"))

        self.user_input_format = config_dict["user_input_format"]

        system_prompt = config_dict["system_prompt"]
        system_prompt = system_prompt.replace("$user_input_format", json.dumps(self.user_input_format))
        self.system_prompt = system_prompt

        example_cases = config_dict["example_cases"]
        assert len(example_cases) % 2 == 0, f"角色对话示例条数必须为偶数"

        history: List[Conversation] = []
        for i in range(0, len(example_cases) - 2, 2):
            user_content = example_cases[i]
            assistant_content = example_cases[i + 1]
            history.append(Conversation(role="user", content=user_content))
            history.append(Conversation(role="assistant", content=assistant_content))

        self.example_cases = history

        logger.info("角色 LLM 配置加载完成")

    def load_tts_prompts(self):
        for dirpath, dirnames, filenames in os.walk(spath("resources/static/audio/momoi")):
            for filename in filenames:
                lang, sentiment, transcript = self.parse_tts_prompt_filename(filename)
                audio_path = str(os.path.join(dirpath, filename))
                tts_prompt = TTSPrompt(audio_path=audio_path, lang=lang, sentiment=sentiment, transcript=transcript)
                self.tts_prompts.append(tts_prompt)
        sentiments = [tts_prompt.sentiment for tts_prompt in self.tts_prompts]

        logger.info(f"角色 TTS 配置加载完成（共 {len(self.tts_prompts)} 条参考语音）：{sentiments}")

    @staticmethod
    def parse_tts_prompt_filename(s: str) -> Tuple[Language, str, str]:
        matches = re.findall(r'\[(.*?)\]', s)

        try:
            lang = Language.value_of(matches[0])
        except ValueError:
            raise ValueError(f"非法的语言标记“{matches[0]}”于字符串“{s}”。")
        except IndexError:
            raise ValueError(f"找不到语言标记于字符串“{s}”。")

        try:
            sentiment = matches[1]
        except ValueError:
            raise ValueError(f"非法的情感标记“{matches[0]}”于字符串“{s}”。")
        except IndexError:
            raise ValueError(f"找不到情感标记于字符串“{s}”。")

        raw_filename = s.replace(f"[{lang.name()}]", "").replace(f"[{sentiment}]", "")
        filetype = raw_filename.split(".")[-1]
        transcript = raw_filename[:-len(f".{filetype}")]

        return lang, sentiment, transcript
