import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from http import HTTPStatus

import requests
from dataclasses_json import dataclass_json
from loguru import logger

from common.abs_app import AppStatusEnum


@dataclass_json
@dataclass
class AbstractModelQuery:
    ...


@dataclass_json
@dataclass
class AbstractModelPrediction:
    ...


@dataclass_json
@dataclass
class ServiceState:
    state: AppStatusEnum
    msg: str


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


@dataclass_json
@dataclass
class AbsractImageModelQuery(AbstractModelQuery):
    img_path: str | None = None


class AbstractImagePipeline(AbstractPipeline):
    def __init__(self):
        super().__init__()
        self.predict_url: str | None = None
        self.stream_predict_url: str | None = None

    def predict(self, query: AbsractImageModelQuery) -> AbstractModelPrediction | None:
        # 如果路径在本机那么就读取，否则认为在远程主机的文件系统中存在
        if os.path.exists(query.img_path):
            files = {'image': open(query.img_path, 'rb')}

            # 将 AbsractImageModelQuery 转化为 JSON 字符串并设置为表单对象
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
