import os
from abc import ABC, abstractmethod
from typing import Tuple, Generator

import requests
from pydantic import BaseModel, Field
from requests import Response
from zerolan.data.pipeline.abs_data import AbsractImageModelQuery, AbstractModelQuery, AbstractModelPrediction


class AbstractPipelineConfig(BaseModel):
    enable: bool = Field(True, description="Whether the pipeline is enabled.")


class PipelineDisabledException(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)


class AbstractPipeline(ABC):

    def __init__(self, config: AbstractPipelineConfig):
        """
        Abstract pipeline.
        Any pipeline (LLMPipeline, etc.) is a subclass of it.
        :param config: An instance used to represent the pipeline configuration.
        """
        assert config is not None, f"Pipeline configuration should not be None."
        # If the pipeline has been disabled, it should not be instantiated
        if not config.enable:
            raise PipelineDisabledException("This pipeline is disabled, to enable it, set `enable` to True")


class PredictablePipeline(AbstractPipeline):
    def __init__(self, config: AbstractPipelineConfig):
        super().__init__(config)
        self.model_id: str = config.model_id
        self.predict_url: str = config.predict_url
        self.stream_predict_url: str = config.stream_predict_url

    @abstractmethod
    def predict(self, query: AbstractModelQuery) -> AbstractModelPrediction:
        raise NotImplementedError("This method has not yet been implemented! Check your implementation of the pipeline")

    @abstractmethod
    def stream_predict(self, query: AbstractModelQuery, chunk_size: int | None = None) -> AbstractModelPrediction:
        raise NotImplementedError("This method has not yet been implemented! Check your implementation of the pipeline")

    @abstractmethod
    def parse_query(self, query: any) -> any:
        raise NotImplementedError("This method has not yet been implemented! Check your implementation of the pipeline")

    @abstractmethod
    def parse_prediction(self, response: Response) -> AbstractModelPrediction:
        raise NotImplementedError("This method has not yet been implemented! Check your implementation of the pipeline")

    @abstractmethod
    def parse_stream_prediction(self, chunk: any) -> AbstractModelPrediction:
        raise NotImplementedError("This method has not yet been implemented! Check your implementation of the pipeline")


class CommonModelPipeline(PredictablePipeline):

    def __init__(self, config: AbstractPipelineConfig):
        super().__init__(config)

    def predict(self, query: AbstractModelQuery) -> AbstractModelPrediction | None:
        """
        Establish HTTP connection and use POST method to get response from the model server.
        Note: This is a sync method so it will block your program.
        :param query: An instance of query. Depend on your model pipeline definition.
        :return: An instance of prediction. Depend on your model pipeline definition. Raise exception if any error happened.
        """
        query_dict = self.parse_query(query)
        response = requests.post(url=self.predict_url, stream=False, json=query_dict)
        response.raise_for_status()
        prediction = self.parse_prediction(response)
        return prediction

    def stream_predict(self, query: AbstractModelQuery, chunk_size: int | None = None) -> Generator[
        AbstractModelPrediction, None, None]:
        """
        Establish HTTP connection and use POST method to get stream response from the model server.
        Note: This is a sync method so it will block your program.
        :param chunk_size: Numbers of bytes per chunk received from stream response.
        :param query: An instance of query. Depend on your model pipeline definition.
        :return: An instance of generator for providing streamed prediction. Depend on your model pipeline definition. Raise exception if any error happened.
        """
        query_dict = self.parse_query(query)
        response = requests.post(url=self.stream_predict_url, stream=True, json=query_dict)
        response.raise_for_status()

        for chunk in response.iter_content(chunk_size=chunk_size, decode_unicode=True):
            prediction = self.parse_stream_prediction(chunk)
            yield prediction

    def parse_query(self, query: any) -> any:
        if isinstance(query, BaseModel):
            query_dict = query.model_dump()
            return query_dict
        else:
            raise NotImplementedError("Unsupported `Query` object parsing method: not a subclass of BaseModel.")

    def parse_prediction(self, response: Response) -> AbstractModelPrediction:
        content = response.content
        assert content is not None, "The HTTP response body contains None content."
        return AbstractModelPrediction.model_validate_json(content)

    def parse_stream_prediction(self, chunk: str) -> AbstractModelPrediction:
        assert chunk is not None, "The HTTP response body contains None chunk."
        return AbstractModelPrediction.model_validate_json(chunk)


class AbstractImagePipeline(CommonModelPipeline):
    def __init__(self, config: any):
        super().__init__(config)

    def predict(self, query: AbsractImageModelQuery) -> AbstractModelPrediction | None:
        response = self._predict(query)
        prediction = self.parse_prediction(response)
        return prediction

    def stream_predict(self, query: AbstractModelQuery, chunk_size: int | None = None) -> Generator[
        AbstractModelPrediction, None, None]:
        response = self._predict(query)
        for chunk in response.iter_content(chunk_size=chunk_size, decode_unicode=True):
            prediction = self.parse_stream_prediction(chunk)
            yield prediction

    def _predict(self, query) -> Response:
        parsed_query = self.parse_query(query)
        response = None
        if isinstance(parsed_query, dict):
            response = requests.post(url=self.predict_url, json=query.model_dump())
        elif isinstance(parsed_query, tuple):
            files, data = parsed_query[0], parsed_query[1]
            response = requests.post(url=self.predict_url, files=files, data=data)
            del files, data

        assert response is not None, "No response got, please check `parse_query`."

        response.raise_for_status()
        return response

    def parse_query(self, query: any) -> Tuple[dict, dict] | dict:
        # If the `query.img_path` path exists on the local machine,
        # then read the image as a binary file and add it to the `request.files`
        if os.path.exists(query.img_path):
            query.img_path = os.path.abspath(query.img_path).replace('\\', '/')
            img = open(query.img_path, 'rb')
            files = {'image': img}
            data = {'json': query.model_dump_json()}

            return files, data
        # If the `query.img_path` path does not exist on the local machine, it must exist on the remote host
        # Note: If the remote host does not have this file neither, raise 500 error!
        else:
            json_dict = query.model_dump()
            return json_dict
