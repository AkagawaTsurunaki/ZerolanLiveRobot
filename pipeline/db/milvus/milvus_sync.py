import json

import requests
from pydantic import BaseModel, Field
from zerolan.data.pipeline.milvus import MilvusInsert, MilvusInsertResult, MilvusQuery, MilvusQueryResult

from pipeline.base.base_sync import AbstractPipeline, AbstractPipelineConfig


class MilvusDatabaseConfig(AbstractPipelineConfig):
    insert_url: str = Field(default="http://127.0.0.1:11000/milvus/insert",
                            description="The URL for inserting data into Milvus.")
    search_url: str = Field(default="http://127.0.0.1:11000/milvus/search",
                            description="The URL for searching data in Milvus.")


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


class MilvusSyncPipeline(AbstractPipeline):
    def __init__(self, config: MilvusDatabaseConfig):
        super().__init__(config)
        self.insert_url = config.insert_url
        self.search_url = config.search_url

    def insert(self, insert: MilvusInsert) -> MilvusInsertResult:
        assert isinstance(insert, MilvusInsert)
        return _post(url=self.insert_url, obj=insert, return_type=MilvusInsertResult)

    def search(self, query: MilvusQuery) -> MilvusQueryResult:
        assert isinstance(query, MilvusQuery)
        return _post(url=self.search_url, obj=query, return_type=MilvusQueryResult)
