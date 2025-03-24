from zerolan.data.pipeline.milvus import InsertRow, MilvusInsert, MilvusQuery

from common.utils.file_util import read_yaml
from ump.pipeline.database import MilvusPipeline, MilvusDatabaseConfig

_config = read_yaml("./resources/config.test.yaml")
pipeline = MilvusPipeline(
    MilvusDatabaseConfig(insert_url=_config['milvus']['insert_url'], search_url=_config['milvus']['search_url']))


def test_insert():
    texts = ["onani就是0721", "柚子厨真恶心", "我喜欢阿米诺！", "0721就是无吟唱水魔法的意思"]
    texts = [InsertRow(id=i, text=texts[i], subject="history") for i in range(len(texts))]
    mi = MilvusInsert(collection_name="Test", texts=texts, drop_if_exists=True)

    ir = pipeline.insert(mi)
    assert ir, "Test failed!"
    print(ir)


def test_search():
    mq = MilvusQuery(collection_name="Test", limit=2, output_fields=["text", 'history'], query="0721是什么意思？")
    qr = pipeline.search(mq)
    assert qr, "Test failed!"
    print(qr)
