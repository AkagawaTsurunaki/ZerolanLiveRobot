import json

from urllib.parse import urljoin

import requests
from pydantic import BaseModel
from zerolan.data.pipeline.milvus import MilvusInsert, MilvusInsertResult, MilvusQuery, MilvusQueryResult

from common.config import MilvusDatabaseConfig
from common.utils.web_util import is_valid_url


def _post(url: str, obj: any, return_type: any):
    if isinstance(obj, BaseModel):
        json_val = obj.model_dump()
    else:
        json_val = obj

    response = requests.post(url=url, json=json_val)
    response.raise_for_status()

    json_val = response.json()
    if hasattr(return_type, "model_validate"):
        return return_type.model_validate(json_val)
    else:
        return json.loads(json_val)


class MilvusPipeline:
    def __init__(self, config: MilvusDatabaseConfig):
        self._server_url: str = config.server_url
        self._insert_url: str = urljoin(config.server_url, '/milvus/insert')
        self._search_url: str = urljoin(config.server_url, '/milvus/search')

        for url in [self._server_url, self._insert_url, self._search_url]:
            assert is_valid_url(url), f"Invalid URL: {url}"

    def insert(self, insert: MilvusInsert) -> MilvusInsertResult:
        return _post(url=self._insert_url, obj=insert, return_type=MilvusInsertResult)

    def search(self, query: MilvusQuery):
        return _post(url=self._search_url, obj=query, return_type=MilvusQueryResult)
