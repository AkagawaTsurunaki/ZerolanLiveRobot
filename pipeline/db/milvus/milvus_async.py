from typeguard import typechecked
from zerolan.data.pipeline.milvus import MilvusQuery, MilvusQueryResult, MilvusInsert, MilvusInsertResult

from pipeline.base.base_async import BaseAsyncPipeline, get_base_url
from pipeline.db.milvus.milvus_sync import MilvusDatabaseConfig


class MilvusAsyncPipeline(BaseAsyncPipeline):
    def __init__(self, config: MilvusDatabaseConfig):
        super().__init__(base_url=get_base_url(config.search_url))
        self._search_endpoint = "/milvus/search"
        self._insert_endpoint = "/milvus/insert"

    @typechecked
    async def search(self, query: MilvusQuery) -> MilvusQueryResult:
        async with self.session.post(self._search_endpoint, json=query.model_dump()) as resp:
            return await resp.json(encoding='utf8', loads=MilvusQueryResult.model_validate_json)

    @typechecked
    async def insert(self, insert: MilvusInsert) -> MilvusInsertResult:
        async with self.session.post(self._insert_endpoint, json=insert.model_dump()) as resp:
            return await resp.json(encoding='utf8', loads=MilvusInsertResult.model_validate_json)
