from typing import Any

from common.abs_model import AbstractModel
from common.config.model_config import ModelConfigLoader
from common.decorator import log_model_loading
from common.register.model_register import LLMModels
from services.llm.pipeline import LLMQuery, Conversation, LLMPrediction
from transformers import AutoModelForCausalLM, AutoTokenizer

config = ModelConfigLoader.yi_model_config


class Yi6B_Chat(AbstractModel):

    def __init__(self):
        super().__init__()
        self._model = None
        self._tokenizer = None
        self.model_id = LLMModels.YI_6B_CHAT.id
        self._model_path = config.model_path
        self._device = config.device

    @log_model_loading(LLMModels.YI_6B_CHAT)
    def load_model(self):
        self._tokenizer = AutoTokenizer.from_pretrained(self._model_path, use_fast=False)
        self._model = AutoModelForCausalLM.from_pretrained(
            self._model_path,
            device_map=self._device,
        ).eval()

    def predict(self, llm_query: LLMQuery) -> Any:
        """
        Yi 6B Chat 推理。
        Args:
            llm_query: 大语言模型的请求，包含请求字符串和历史记录。

        Returns:
            大语言模型推理体，包含回应和历史记录。

        """
        messages = self._to_yi_format(llm_query)
        # 如果报错
        # AttributeError: 'LlamaTokenizer' object has no attribute 'apply_chat_template'
        # 请查看这里 https://github.com/01-ai/Yi/issues/241
        # > Please check the version of transformers and make sure it is 4.35.0 or above.
        input_ids = self._tokenizer.apply_chat_template(conversation=messages, tokenize=True,
                                                        add_generation_prompt=True,
                                                        return_tensors='pt').to('cuda')
        output_ids = self._model.generate(input_ids)
        response = self._tokenizer.decode(output_ids[0][input_ids.shape[1]:], skip_special_tokens=True)

        return self._to_pipeline_format(response, messages)

    def stream_predict(self, *args, **kwargs) -> Any:
        """
        Yi 6B Chat 流式推理。
        Args:
            llm_query: 大语言模型的请求，包含请求字符串和历史记录。

        Returns:
            生成器。大语言模型推理体，包含回应和历史记录。

        """
        raise NotImplementedError('Yi 6B Chat 暂时不支持流式推理')

    @staticmethod
    def _to_yi_format(llm_query: LLMQuery):
        messages = [{"role": c.role, "content": c.content} for c in llm_query.history]
        messages.append({"role": "user", "content": llm_query.text})
        return messages

    @staticmethod
    def _to_pipeline_format(response, messages):
        messages.append({"role": "assistant", "content": response})
        history = [Conversation(role=c['role'], content=c['content']) for c in messages]
        return LLMPrediction(response, history)
