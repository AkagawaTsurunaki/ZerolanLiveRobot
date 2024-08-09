"""
详细请见：
    https://huggingface.co/Qwen/Qwen-7B-Chat
"""
from typing import Any

from loguru import logger

from common.abs_model import AbstractModel
from common.config.model_config import ModelConfigLoader
from common.decorator import log_model_loading
from common.register.model_register import LLMModels
from transformers import AutoModelForCausalLM, AutoTokenizer

from services.llm.pipeline import LLMQuery, LLMPrediction, Conversation

config = ModelConfigLoader.qwen_model_config


class Qwen7BChat(AbstractModel):

    def __init__(self):
        super().__init__()

        self.model_id = LLMModels.QWEN_7B_CHAT.id
        self._model_path = config.model_path
        logger.warning(f'⚠️ 模型 {self.model_id} 使用多卡推理可能会报错，因此您应该使用单卡。')
        self._device = config.device
        self._precise = config.precise

        self._model: any = None
        self._tokenizer: any = None

    @log_model_loading(LLMModels.QWEN_7B_CHAT)
    def load_model(self):
        self._tokenizer = AutoTokenizer.from_pretrained(self._model_path, trust_remote_code=True)
        if self._precise == "bf16":
            self._model = AutoModelForCausalLM.from_pretrained(self._model_path,
                                                               device_map=self._device,
                                                               trust_remote_code=True,
                                                               bf16=True)
        elif self._precise == "fp16":
            self._model = AutoModelForCausalLM.from_pretrained(self._model_path,
                                                               device_map=self._device,
                                                               trust_remote_code=True,
                                                               fp16=True)
        else:
            self._model = AutoModelForCausalLM.from_pretrained(self._model_path,
                                                               device_map=self._device,
                                                               trust_remote_code=True)
        assert self._tokenizer and self._model

    def predict(self, llm_query: LLMQuery) -> LLMPrediction:
        """
        Qwen 7B Chat 推理。
        Args:
            llm_query: 大语言模型的请求，包含请求字符串和历史记录。

        Returns:
            大语言模型推理体，包含回应和历史记录。

        """
        text, history, sys_prompt = self._to_qwen_format(llm_query)
        response, history = self._model.chat(self._tokenizer, llm_query.text, history=history)
        logger.debug(response)
        return self._to_pipeline_format(response, history, sys_prompt)

    def stream_predict(self, llm_query: LLMQuery) -> Any:
        """
        Qwen 7B Chat 流式推理。
        Args:
            llm_query: 大语言模型的请求，包含请求字符串和历史记录。

        Returns:
            生成器。大语言模型推理体，包含回应和历史记录。

        """
        text, history, sys_prompt = self._to_qwen_format(llm_query)
        history.append((text, ""))
        # 如果报错
        # typeError: isin() received an invalid combination of arguments - got (test_elements=int, elements=Tensor,), but expected one of...
        # 请查看这里
        # https://github.com/QwenLM/Qwen-VL/issues/407
        # `pip install transformers==4.32.0`
        for response in self._model.chat_stream(self._tokenizer, llm_query.text, history=history):
            logger.debug(response)
            history[-1] = (text, response)

    @staticmethod
    def _to_qwen_format(llm_query: LLMQuery) -> (str, list[tuple[str, str]], str):
        history_content_list: list[str] = [c.content for c in llm_query.history]

        sys_prompt = None
        history = []
        # 拼接系统提示词
        if len(llm_query.history) > 0:
            if llm_query.history[0].role == "system":
                sys_prompt = llm_query.history[0].content
                if len(history_content_list) > 0:
                    history_content_list = history_content_list[1:]
                    history_content_list[0] = sys_prompt + history_content_list[0]

            assert len(history_content_list) % 2 == 0, f'必须为偶数'

            # 转化为 tuple
            history: list[tuple] = []

            for i in range(0, len(history_content_list), 2):
                history.append((history_content_list[i], history_content_list[i + 1]))

        text = llm_query.text
        return text, history, sys_prompt

    @staticmethod
    def _to_pipeline_format(response: str, history: list[tuple[str, str]], sys_prompt: str) -> LLMPrediction:
        # 将 history 转化为 pipeline 的格式
        ret_history: list[Conversation] = []
        for chat in history:
            q, r = chat[0], chat[1]
            assert isinstance(q, str) and isinstance(r, str)
            ret_history.append(Conversation(role="user", content=q))
            ret_history.append(Conversation(role="assistant", content=r))

        # 获取系统提示词
        if sys_prompt:
            ret_history[0].content = ret_history[0].content[len(sys_prompt):]
            ret_history.insert(0, Conversation(role="system", content=sys_prompt))

        llm_response = LLMPrediction(response=response, history=ret_history)

        return llm_response
