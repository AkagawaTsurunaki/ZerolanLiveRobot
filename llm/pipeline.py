import json
from dataclasses import asdict
from http import HTTPStatus
from urllib.parse import urljoin

import requests
from loguru import logger

from config import GLOBAL_CONFIG as G_CFG
from utils.datacls import LLMQuery, Chat, LLMResponse, ServiceNameConst as SNR


class LLMPipeline:

    def __init__(self):
        config = G_CFG.large_language_model
        model = next(iter(config.models))
        self.model_list = [SNR.CHATGLM3, SNR.YI, SNR.QWEN, SNR.SHISA]
        assert model in self.model_list, f'Unsupported model "{model}".'
        self.model = model

        url = f'http://{config.host}:{config.port}'
        self.predict_url = urljoin(url, f'/llm/predict')
        self.stream_predict_url = urljoin(url, f'/llm/stream-predict')

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
