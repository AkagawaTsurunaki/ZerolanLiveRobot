from copy import deepcopy

from zerolan.data.data.llm import Conversation, RoleEnum

from common.config import ChatConfig


class LLMPromptManager:
    def __init__(self, config: ChatConfig):
        self.system_prompt: str = config.system_prompt
        self.injected_history: list[Conversation] = self._parse_history_list(config.injected_history,
                                                                             self.system_prompt)
        self.current_history: list[Conversation] = deepcopy(self.injected_history)
        self.max_history = config.max_history

    def reset_history(self, history: list[Conversation]) -> None:
        """
        Resets `current_history` with deepcopy.
        If the length of `current_history` is greater than the `max_history`,
        resets it to `injected_history` from the config file.
        :param history: List of instances of class Conversation
        :return: None
        """
        if history is None:
            self.current_history = deepcopy(self.injected_history)
        else:
            if len(history) <= self.max_history:
                self.current_history = deepcopy(history)
            else:
                self.current_history = deepcopy(self.injected_history)

    @staticmethod
    def _parse_history_list(history: list[str], system_prompt: str | None = None) -> list[Conversation]:
        result = []

        if system_prompt is not None:
            result.append(Conversation(role=RoleEnum.system, content=system_prompt))

        for idx, content in enumerate(history):
            role = RoleEnum.user if idx % 2 == 0 else RoleEnum.assistant
            conversation = Conversation(role=role, content=content)
            result.append(conversation)

        return result
