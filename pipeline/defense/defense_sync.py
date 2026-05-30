from openai import OpenAI
from requests import Response
from typeguard import typechecked
from zerolan.data.pipeline.llm import LLMQuery, LLMPrediction, RoleEnum, Conversation

from pipeline.base.base_sync import CommonModelPipeline
from pipeline.defense.config import DefenseModelPipelineConfig


def _to_openai_format(query: LLMQuery):
    messages = []
    for chat in query.history:
        messages.append({
            "role": chat.role,
            "content": chat.content
        })
    messages.append({
        "role": "user",
        "content": query.text
    })
    return messages


def _openai_predict(query: LLMQuery, wrapper):
    messages = _to_openai_format(query)
    completion = wrapper(messages)
    resp = completion.choices[0].message.content
    query.history.append(Conversation(role=RoleEnum.user, content=query.text))
    query.history.append(Conversation(role=RoleEnum.assistant, content=resp))
    return LLMPrediction(response=resp, history=query.history)


"""
命名方式: 该类默认为防御大语言模型 DefenseLLM 的管道，若为非大语言模型架构可自行创建新类 Defense
"""
class DefenseLLMSyncPipeline(CommonModelPipeline):

    def __init__(self, config: DefenseModelPipelineConfig):
        super().__init__(config)
        self._is_openai_format = config.openai_format
        if self._is_openai_format:
            assert config.predict_url and config.stream_predict_url, "Please provide `predict_url` or `stream_predict_url`"
            base_url = config.predict_url if config.predict_url else config.stream_predict_url
            self._remote_model = OpenAI(api_key=config.api_key, base_url=base_url)

    @typechecked
    def predict(self, query: LLMQuery) -> LLMPrediction | None:
        assert isinstance(query, LLMQuery)
        if self._is_openai_format:
            # example
            if self.model_id == "xxx":
                def wrapper_xxx(messages):
                    return self._remote_model.chat.completions.create(
                        model=self.model_id,
                        messages=messages,
                        stream=False
                    )

                return _openai_predict(query, wrapper_xxx)
            else:
                raise NotImplementedError(f"Unsupported model {self.model_id}")
        else:
            return super().predict(query)

    @typechecked
    def stream_predict(self, query: LLMQuery, chunk_size: int | None = None):
        assert isinstance(query, LLMQuery)
        return super().stream_predict(query)

    def parse_prediction(self, response: Response) -> LLMPrediction:
        json_val = response.content
        return LLMPrediction.model_validate_json(json_val)
