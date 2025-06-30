from config import get_config
from zerolan.data.pipeline.milvus import InsertRow, MilvusInsert, MilvusQuery

from pipeline.db.milvus.milvus_sync import MilvusSyncPipeline

_config = get_config()
pipeline = MilvusSyncPipeline(config=_config.pipeline.vec_db.milvus)


def test_insert():
    texts = ["onani就是0721", "柚子厨真恶心", "我喜欢阿米诺！", "0721就是无吟唱水魔法的意思"]
    texts = [InsertRow(id=i, text=texts[i], subject="history") for i in range(len(texts))]
    mi = MilvusInsert(collection_name="Test", texts=texts, drop_if_exists=True)

    ir = pipeline.insert(mi)
    print(ir)


def test_search():
    mq = MilvusQuery(collection_name="Test", limit=2, output_fields=["text", 'history'], query="0721是什么意思？")
    qr = pipeline.search(mq)
    print(qr)
