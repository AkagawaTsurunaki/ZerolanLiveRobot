from dataclasses import asdict
from http import HTTPStatus
from typing import List
from utils import util
from urllib.parse import urljoin

import requests

import chatglm3.api
import initzr
from utils.datacls import NewLLMQuery, Chat, NewLLMResponse
from loguru import logger


class LLMPipeline:

    def __init__(self, model: str):
        url = initzr.load_llm_service_config().url()
        self.predict_url = urljoin(url, '/predict')
        self.model_list = ['chatglm3', '01-ai/Yi', 'Qwen/Qwen-7B-Chat']
        assert model in self.model_list, f'Unsupported model "{model}".'
        self.model = model
        self.model_query_map = {
            'chatglm3': LLMPipeline.chatglm3,
            '01-ai/Yi': LLMPipeline.yi,
            'Qwen/Qwen-7B-Chat': LLMPipeline.qwen
        }

    @staticmethod
    def chatglm3(llm_query: NewLLMQuery) -> dict:
        # Convert to ChatGLM3 format
        text = llm_query.text
        history = [{'role': chat.role, 'metadata': '', 'content': chat.content} for chat in llm_query.history]

        # Add query
        result = {
            'query': text,
            'history': history
        }

        return result

    @staticmethod
    def yi(llm_query: NewLLMQuery) -> list:
        # Convert to Yi format
        text = llm_query.text
        history = [{'role': chat.role, 'content': chat.content} for chat in llm_query.history]

        # Add query
        result = history + [{'role': 'user', 'content': text}]

        return result

    @staticmethod
    def qwen(llm_query: NewLLMQuery) -> list:
        # Convert to Qwen format
        text = llm_query.text
        history = [{'role': chat.role, 'content': chat.content} for chat in llm_query.history]

        # Add query
        result = history + [{'role': 'user', 'content': text}]

        return result

    def query(self, llm_query: NewLLMQuery) -> any:
        query_func = self.model_query_map.get(self.model, None)
        assert query_func
        return query_func(llm_query)

    def predict(self, query: any):
        if self.model == self.model_list[0]:
            # ChatGLM3
            chatglm3.api.predict(**query)
        elif self.model == self.model_list[1]:
            # Yi
            ...
        elif self.model == self.model_list[2]:
            # Qwen
            ...

    def response(self):
        if len(self.history) > 0:
            if self.model == self.model_list[0]:
                # ChatGLM3
                return self.history[-1].get('content', None)
            elif self.model == self.model_list[1]:
                # Yi
                return self.history[-1].get('content', None)
            elif self.model == self.model_list[2]:
                # Qwen
                return self.history[-1].get('content', None)

    @staticmethod
    def convert_query_from_json(json_val: any) -> NewLLMQuery:
        history = json_val['history']
        history = [Chat(role=chat['role'], content=chat['content']) for chat in history]
        llm_query = NewLLMQuery(
            text=json_val['text'],
            history=history
        )
        return llm_query

    @staticmethod
    def convert_response_from_json(json_val: any) -> NewLLMResponse:
        response = json_val['response']
        history = json_val['history']
        history = [Chat(role=chat['role'], content=chat['content']) for chat in history]
        llm_response = NewLLMResponse(
            response=response,
            history=history
        )
        return llm_response

    def predict(self, llm_query: NewLLMQuery) -> NewLLMResponse | None:
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

    def predict_without_history(self, plain_text: str):
        llm_query = NewLLMQuery(
            text=plain_text,
            history=[]
        )
        return self.predict(llm_query)

    def load_prompt_template(self, path: str):
        json_val = util.read_json(path)
        llm_query = LLMPipeline.convert_query_from_json(json_val)
        return llm_query
