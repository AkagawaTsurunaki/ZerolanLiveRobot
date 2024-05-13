from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from http import HTTPStatus
from loguru import logger

import requests


@dataclass
class AbstractModelQuery:
    ...


@dataclass
class AbstractModelResponse:
    ...


class AbstractPipeline(ABC):

    def __init__(self):
        self.predict_url: str | None = None

    @abstractmethod
    def predict(self, query: AbstractModelQuery) -> AbstractModelResponse | None:
        try:
            query_dict = asdict(query)
            response = requests.post(url=self.predict_url, stream=True, json=query_dict)
            if response.status_code == HTTPStatus.OK:
                json_val = response.json()
                response = self.parse_response_from_json(json_val)
                return response
        except Exception as e:
            logger.exception(e)
            return None

    @staticmethod
    def parse_response_from_json(obj: any) -> AbstractModelResponse:
        raise TypeError('Methods must be overridden by inherited class.')

    @staticmethod
    def parse_query_from_json(obj: any) -> AbstractModelQuery:
        raise TypeError('Methods must be overridden by inherited class.')
