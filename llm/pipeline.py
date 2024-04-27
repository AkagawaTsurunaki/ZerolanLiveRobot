import json
from dataclasses import asdict
from urllib.parse import urljoin

import requests

from common.abs_pipeline import AbstractPipeline
from config import GlobalConfig
from common.datacls import LLMQuery, Chat, LLMResponse


class LLMPipeline(AbstractPipeline):

    def __init__(self, cfg: GlobalConfig):
        super().__init__()
        self.model = cfg.large_language_model.models[0].model_name
        host, port = cfg.large_language_model.host, cfg.large_language_model.port
        url = f'http://{host}:{port}'
        self.predict_url = urljoin(url, f'/llm/predict')
        self.stream_predict_url = urljoin(url, f'/llm/stream-predict')

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
