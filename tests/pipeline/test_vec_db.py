import pytest
from zerolan.data.pipeline.milvus import InsertRow, MilvusInsert, MilvusQuery

from manager.config_manager import get_config
from pipeline.db.milvus.milvus_async import MilvusAsyncPipeline
from pipeline.db.milvus.milvus_sync import MilvusSyncPipeline

_config = get_config()
_milvus_async = MilvusAsyncPipeline(_config.pipeline.vec_db)
_milvus_sync = MilvusSyncPipeline(_config.pipeline.vec_db)


@pytest.mark.asyncio
async def test_insert():
    texts = ["onani就是0721", "柚子厨真恶心", "我喜欢阿米诺！", "0721就是无吟唱水魔法的意思"]
    texts = [InsertRow(id=i, text=texts[i], subject="history") for i in range(len(texts))]
    mi = MilvusInsert(collection_name="Test", texts=texts, drop_if_exists=True)

    ir = await _milvus_async.insert(mi)
    assert ir, "Test failed!"
    print(ir)


@pytest.mark.asyncio
async def test_search():
    mq = MilvusQuery(collection_name="Test", limit=2, output_fields=["text", 'history'], query="0721是什么意思？")
    qr = await _milvus_async.search(mq)
    assert qr, "Test failed!"
    print(qr)


def test_insert_sync():
    texts = ["onani就是0721", "柚子厨真恶心", "我喜欢阿米诺！", "0721就是无吟唱水魔法的意思"]
    texts = [InsertRow(id=i, text=texts[i], subject="history") for i in range(len(texts))]
    mi = MilvusInsert(collection_name="Test", texts=texts, drop_if_exists=True)

    ir = _milvus_sync.insert(mi)
    assert ir, "Test failed!"
    print(ir)


def test_search_sync():
    mq = MilvusQuery(collection_name="Test", limit=2, output_fields=["text", 'history'], query="0721是什么意思？")
    qr = _milvus_sync.search(mq)
    assert qr, "Test failed!"
    print(qr)
