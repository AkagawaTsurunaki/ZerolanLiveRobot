import json
from dataclasses import asdict, dataclass
from typing import List
from urllib.parse import urljoin

import requests

from common.abs_pipeline import AbstractPipeline, AbstractModelQuery, AbstractModelResponse
from config import GlobalConfig
from common import util


@dataclass
class Chat:
    role: str
    content: str


@dataclass
class LLMQuery(AbstractModelQuery):
    text: str
    history: List[Chat]


@dataclass
class LLMResponse(AbstractModelResponse):
    response: str
    history: List[Chat]


@dataclass
class Role:
    USER = 'user'
    ASSISTANT = 'assistant'
    SYSTEM = 'system'


class LLMPipeline(AbstractPipeline):

    def __init__(self, cfg: GlobalConfig):
        super().__init__()
        self.model = cfg.large_language_model.models[0].model_name
        host, port = cfg.large_language_model.host, cfg.large_language_model.port
        self.predict_url = util.urljoin(host, port, '/llm/predict')
        self.stream_predict_url = util.urljoin(host, port, f'/llm/stream-predict')

    def predict(self, query: LLMQuery) -> LLMResponse | None:
        return super().predict(query)

    @staticmethod
    def parse_query_from_json(obj: any) -> LLMQuery:
        history = obj['history']
        history = [Chat(role=chat['role'], content=chat['content']) for chat in history]
        llm_query = LLMQuery(
            text=obj['text'],
            history=history
        )
        return llm_query

    @staticmethod
    def parse_response_from_json(obj: any) -> LLMResponse:
        response = obj['response']
        history = obj['history']
        history = [Chat(role=chat['role'], content=chat['content']) for chat in history]
        llm_response = LLMResponse(
            response=response,
            history=history
        )
        return llm_response

    async def stream_predict(self, llm_query: LLMQuery):
        llm_query = asdict(llm_query)
        response = requests.get(url=self.stream_predict_url, stream=True,
                                json=llm_query)

        for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
            json_val = json.loads(chunk)
            llm_response = LLMPipeline.parse_response_from_json(json_val)
            yield llm_response
