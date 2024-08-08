"""
详细请见：
    https://github.com/THUDM/ChatGLM3
"""
from loguru import logger
from transformers import AutoTokenizer, AutoModel

from common.abs_model import AbstractModel
from common.config.model_config import ModelConfigLoader
from common.decorator import log_model_loading
from common.register.model_register import LLMModels
from services.llm.pipeline import LLMQuery, LLMPrediction, Conversation

config = ModelConfigLoader.chatglm3_model_config


class ChatGLM3_6B(AbstractModel):

    def __init__(self):
        super().__init__()
        self.model_id = LLMModels.CHATGLM3_6B.id
        self._model_path = config.model_path
        self._quantize = config.quantize
        self._device = config.device

        self._tokenizer: any = None
        self._model: any = None

    @log_model_loading(LLMModels.CHATGLM3_6B)
    def load_model(self):

        self._tokenizer = AutoTokenizer.from_pretrained(self._model_path, trust_remote_code=True)
        if self._quantize:
            self._model = AutoModel.from_pretrained(self._model_path, trust_remote_code=True).quantize(
                self._quantize).to(
                self._device).eval()
            logger.info(f"模型量化至 {self._quantize}")
        else:
            self._model = AutoModel.from_pretrained(self._model_path, trust_remote_code=True).to(self._device).eval()
            logger.info(f"模型以非量化模式启动")
        assert self._tokenizer and self._model

    def predict(self, llm_query: LLMQuery) -> LLMPrediction:
        """
        ChatGLM3 6B 推理。
        Args:
            llm_query: 大语言模型的请求，包含请求字符串和历史记录。

        Returns:
            大语言模型推理体，包含回应和历史记录。

        """
        text, history = self._to_chatglm_format(llm_query)
        # 注意：在新版本中 past_key_values=None 会引发索引错误，
        # 因为底层代码中不会判断 past_key_values 是否为 None，
        # 而是只要有 past_key_values 这个参数就尝试解析
        response, history = self._model.chat(self._tokenizer, text, history, top_p=1., temperature=1.)
        logger.debug(response)
        return self._to_pipeline_format(response, history)

    def stream_predict(self, llm_query: LLMQuery):
        """
        ChatGLM3 6B 流式推理。
        Args:
            llm_query: 大语言模型的请求，包含请求字符串和历史记录。

        Returns:
            生成器。大语言模型推理体，包含回应和历史记录。

        """
        text, history = self._to_chatglm_format(llm_query)
        for response, history, past_key_values in self._model.stream_chat(self._tokenizer, text, history=history,
                                                                          top_p=1.,
                                                                          temperature=1.,
                                                                          past_key_values=None,
                                                                          return_past_key_values=True):
            logger.debug(response)
            yield self._to_pipeline_format(response, history)

    @staticmethod
    def _to_chatglm_format(llm_query: LLMQuery) -> (str, list[dict[str:str]]):
        text = llm_query.text
        history = [{'role': chat.role, 'metadata': '', 'content': chat.content} for chat in llm_query.history]
        return text, history

    @staticmethod
    def _to_pipeline_format(response: str, history: list[dict[str:str]]) -> LLMPrediction:
        history = [Conversation(role=chat['role'], content=chat['content']) for chat in history]
        llm_response = LLMPrediction(response=response, history=history)
        return llm_response
