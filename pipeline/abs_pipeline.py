import os
from abc import ABC, abstractmethod
from http import HTTPStatus

import requests
from loguru import logger

from zerolan_live_robot_core.abs_app import AppStatusEnum
from zerolan_live_robot_data.abs_data import AbsractImageModelQuery, AbstractModelQuery, AbstractModelPrediction, \
    ServiceState


class AbstractPipeline(ABC):

    def __init__(self):
        self.predict_url: str | None = None
        self.stream_predict_url: str | None = None
        self.state_url: str | None = None

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

    @abstractmethod
    def parse_query(self, query: any) -> dict:
        raise NotImplementedError()

    @abstractmethod
    def parse_prediction(self, json_val: any) -> AbstractModelPrediction:
        raise NotImplementedError()

    def check_state(self) -> ServiceState:
        try:
            response = requests.get(url=self.state_url, stream=True)
            if response.status_code == HTTPStatus.OK:
                state = ServiceState.from_json(response.content)
                return state
        except Exception as e:
            logger.error(e)
            return ServiceState(state=AppStatusEnum.UNKNOWN, msg=f"{e}")


class AbstractImagePipeline(AbstractPipeline):
    def __init__(self):
        super().__init__()
        self.predict_url: str | None = None
        self.stream_predict_url: str | None = None

    def predict(self, query: AbsractImageModelQuery) -> AbstractModelPrediction | None:
        # If the path is native then it is read, otherwise it is considered to exist in the remote host's file system
        if os.path.exists(query.img_path):
            files = {'image': open(query.img_path, 'rb')}

            # Convert AbsractImageModelQuery to a JSON string and set it as a form object
            assert hasattr(query, "to_json")
            data = {'json': query.to_json()}  # type: ignore

            response = requests.post(url=self.predict_url, files=files, data=data)
        else:
            response = requests.post(url=self.predict_url, json=query.to_dict())  # type: ignore
        if response.status_code == HTTPStatus.OK:
            prediction = self.parse_prediction(response.content)
            return prediction
        else:
            response.raise_for_status()

    @abstractmethod
    def stream_predict(self, query: AbstractModelQuery):
        raise NotImplementedError()

    @abstractmethod
    def parse_query(self, query: any) -> dict:
        raise NotImplementedError()

    @abstractmethod
    def parse_prediction(self, json_val: any) -> AbstractModelPrediction:
        raise NotImplementedError()
