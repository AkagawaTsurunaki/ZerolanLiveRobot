import json
from abc import ABC, abstractmethod
from typing import List

from loguru import logger
from zerolan.data.data.llm import Conversation

from common.data.prompt import TTSPrompt
from common.utils.file_util import read_yaml, spath


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
        self.bad_words = []

    def load_filter_config(self):
        config_dict = read_yaml(spath("resources/config/chat_config.yaml"))
        self.bad_words = config_dict["bad_words"]

    def load_config(self):
        super().load_config()
        self.load_filter_config()

    def load_llm_prompts(self):

        config_dict = read_yaml(spath("resources/config/chat_config.yaml"))

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




