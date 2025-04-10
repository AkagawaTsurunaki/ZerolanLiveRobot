import pytest
from zerolan.data.pipeline.milvus import InsertRow, MilvusInsert, MilvusQuery

from private import base_url
from pipeline.db.milvus_async import MilvusPipeline

_milvus = MilvusPipeline(base_url=base_url)


@pytest.mark.asyncio
async def test_insert():
    texts = ["onani就是0721", "柚子厨真恶心", "我喜欢阿米诺！", "0721就是无吟唱水魔法的意思"]
    texts = [InsertRow(id=i, text=texts[i], subject="history") for i in range(len(texts))]
    mi = MilvusInsert(collection_name="Test", texts=texts, drop_if_exists=True)

    ir = await _milvus.insert(mi)
    assert ir, "Test failed!"
    print(ir)

@pytest.mark.asyncio
async def test_search():
    mq = MilvusQuery(collection_name="Test", limit=2, output_fields=["text", 'history'], query="0721是什么意思？")
    qr = await _milvus.search(mq)
    assert qr, "Test failed!"
    print(qr)
