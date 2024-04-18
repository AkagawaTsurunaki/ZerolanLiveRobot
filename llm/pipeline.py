import json
from dataclasses import asdict
from http import HTTPStatus
from urllib.parse import urljoin

import requests
from loguru import logger

import initzr
from utils.datacls import LLMQuery, Chat, LLMResponse


class LLMPipeline:

    def __init__(self):
        model = initzr.load_llm_service_config().llm_name
        self.model_list = ['chatglm3', '01-ai/Yi', 'Qwen/Qwen-7B-Chat']
        assert model in self.model_list, f'Unsupported model "{model}".'
        self.model = model

        url = initzr.load_llm_service_config().url()
        self.predict_url = urljoin(url, f'/{self.model}/predict')
        self.stream_predict_url = urljoin(url, f'/{self.model}/stream-predict')

    @staticmethod
    def convert_query_from_json(json_val: any) -> LLMQuery:
        history = json_val['history']
        history = [Chat(role=chat['role'], content=chat['content']) for chat in history]
        llm_query = LLMQuery(
            text=json_val['text'],
            history=history
        )
        return llm_query

    @staticmethod
    def convert_response_from_json(json_val: any) -> LLMResponse:
        response = json_val['response']
        history = json_val['history']
        history = [Chat(role=chat['role'], content=chat['content']) for chat in history]
        llm_response = LLMResponse(
            response=response,
            history=history
        )
        return llm_response

    def predict(self, llm_query: LLMQuery) -> LLMResponse | None:
        try:
            llm_query = asdict(llm_query)
            response = requests.get(url=self.predict_url, stream=True, json=llm_query)
            if response.status_code == HTTPStatus.OK:
                json_val = response.json()
                llm_response = LLMPipeline.convert_response_from_json(json_val)
                return llm_response
        except Exception as e:
            logger.exception(e)
            return None

    async def stream_predict(self, llm_query: LLMQuery):

        llm_query = asdict(llm_query)
        response = requests.get(url=self.stream_predict_url, stream=True,
                                json=llm_query)

        for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
            json_val = json.loads(chunk)
            llm_response = LLMPipeline.convert_response_from_json(json_val)
            yield llm_response
