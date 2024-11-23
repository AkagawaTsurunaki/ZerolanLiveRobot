import os
from abc import ABC, abstractmethod
from http import HTTPStatus

import requests
from loguru import logger
from pydantic import BaseModel
from zerolan.data.data.state import AppStatusEnum, ServiceState
from zerolan.data.pipeline.abs_data import AbsractImageModelQuery, AbstractModelQuery, AbstractModelPrediction

from common.utils.web_util import is_valid_url


class AbstractPipeline(ABC):

    def __init__(self, config: any):
        self.config = config
        self.is_pipeline_enable()
        self.predict_url: str | None = None
        self.stream_predict_url: str | None = None
        self.state_url: str | None = None

    def is_pipeline_enable(self):
        if not self.config.enable:
            raise Exception("The pipeline is disabled in your config!")

    def check_urls(self):
        urls = {"predict_url": self.predict_url,
                "stream_predict_url": self.stream_predict_url,
                "state_url": self.state_url}
        for url_name, url in urls.items():
            if url is None:
                raise ValueError(f"No {url_name} URL was provided.")
            if not is_valid_url(url):
                raise ValueError(f"Invalid URL: {url}")

    @abstractmethod
    def predict(self, query: AbstractModelQuery) -> AbstractModelPrediction | None:
        query_dict = self.parse_query(query)
        response = requests.post(url=self.predict_url, stream=True, json=query_dict)
        if response.status_code == HTTPStatus.OK:
            prediction = self.parse_prediction(response.content)
            return prediction
        else:
            response.raise_for_status()

    @abstractmethod
    def stream_predict(self, query: AbstractModelQuery):
        query_dict = self.parse_query(query)
        response = requests.get(url=self.stream_predict_url, stream=True,
                                json=query_dict)

        if response.status_code == HTTPStatus.OK:
            for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                prediction = self.parse_prediction(chunk)
                yield prediction
        else:
            response.raise_for_status()

    def parse_query(self, query: any) -> dict:
        if isinstance(query, BaseModel):
            return query.model_dump()
        else:
            raise ValueError("Query must be an instance of BaseModel.")

    @abstractmethod
    def parse_prediction(self, json_val: any) -> AbstractModelPrediction:
        raise NotImplementedError()

    def check_state(self) -> ServiceState:
        try:
            response = requests.get(url=self.state_url, stream=True)
            if response.status_code == HTTPStatus.OK:
                state = ServiceState.model_validate_json(response.content)
                return state
        except Exception as e:
            logger.error(e)
            return ServiceState(state=AppStatusEnum.UNKNOWN, msg=f"{e}")


class AbstractImagePipeline(AbstractPipeline):
    def __init__(self, config: any):
        super().__init__(config)
        self.predict_url: str | None = None
        self.stream_predict_url: str | None = None

    def predict(self, query: AbsractImageModelQuery) -> AbstractModelPrediction | None:
        # If the path is native then it is read, otherwise it is considered to exist in the remote host's file system
        if os.path.exists(query.img_path):
            files = {'image': open(query.img_path, 'rb')}

            # Convert AbsractImageModelQuery to a JSON string and set it as a form object
            data = {'json': query.model_dump_json()}

            response = requests.post(url=self.predict_url, files=files, data=data)
        else:
            response = requests.post(url=self.predict_url, json=query.model_dump())
        if response.status_code == HTTPStatus.OK:
            prediction = self.parse_prediction(response.content)
            return prediction
        else:
            response.raise_for_status()

    @abstractmethod
    def stream_predict(self, query: AbstractModelQuery):
        raise NotImplementedError()

    def parse_query(self, query: any) -> dict:
        raise NotImplementedError()

    @abstractmethod
    def parse_prediction(self, json_val: any) -> AbstractModelPrediction:
        raise NotImplementedError()
