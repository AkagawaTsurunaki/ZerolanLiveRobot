from openai import OpenAI
from pydantic import Field
from requests import Response
from zerolan.data.pipeline.abs_data import AbstractModelQuery
from zerolan.data.pipeline.llm import LLMQuery, LLMPrediction, RoleEnum, Conversation

from ump.abs_pipeline import CommonModelPipeline, AbstractPipelineConfig


class LLMPipelineConfig(AbstractPipelineConfig):
    api_key: str | None = Field(default=None, description="The API key for accessing the LLM service.　\n"
                                                          "Kimi API supported: \n"
                                                          "Reference: https://platform.moonshot.cn/docs/guide/start-using-kimi-api \n"
                                                          "Deepseek API supported: \n"
                                                          "Reference: https://api-docs.deepseek.com/zh-cn/")
    openai_format: bool = Field(default=False, description="Whether the output format is compatible with OpenAI. \n"
                                                           "Note: When you use Kimi API or Deepseek API, please set it `true`.")
    model_id: str = Field(default="", description="The ID of the model used for LLM.")
    predict_url: str = Field(default="http://127.0.0.1:11000/llm/predict",
                             description="The URL for LLM prediction requests.")
    stream_predict_url: str = Field(default="http://127.0.0.1:11000/llm/stream-predict",
                                    description="The URL for streaming LLM prediction requests.")

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


class LLMPipeline(CommonModelPipeline):

    def __init__(self, config: LLMPipelineConfig):
        super().__init__(config)
        # Kimi API supported
        # Reference: https://platform.moonshot.cn/docs/guide/start-using-kimi-api
        # Deepseek API supported
        # Reference: https://api-docs.deepseek.com/zh-cn/
        self._is_openai_format = config.openai_format
        if self._is_openai_format:
            assert config.predict_url and config.stream_predict_url, "Please provide `predict_url` or `stream_predict_url`"
            base_url = config.predict_url if config.predict_url else config.stream_predict_url
            self._remote_model = OpenAI(api_key=config.api_key, base_url=base_url)

    def predict(self, query: LLMQuery) -> LLMPrediction | None:
        assert isinstance(query, LLMQuery)
        if self._is_openai_format:
            if self.model_id == "moonshot-v1-8k":
                def wrapper_kimi(messages):
                    return self._remote_model.chat.completions.create(
                        model=self.model_id,
                        messages=messages,
                        temperature=0.3
                    )

                return _openai_predict(query, wrapper_kimi)
            elif self.model_id == "deepseek-chat":
                def wrapper_deepseek(messages):
                    return self._remote_model.chat.completions.create(
                        model=self.model_id,
                        messages=messages,
                        stream=False
                    )

                return _openai_predict(query, wrapper_deepseek)
            else:
                raise NotImplementedError(f"Unsupported model {self.model_id}")
        else:
            return super().predict(query)

    def stream_predict(self, query: LLMQuery, chunk_size: int | None = None):
        assert isinstance(query, LLMQuery)
        # TODO: Kimi and Deepseek stream prediction.
        return super().stream_predict(query)

    def parse_prediction(self, response: Response) -> LLMPrediction:
        json_val = response.content
        return LLMPrediction.model_validate_json(json_val)
