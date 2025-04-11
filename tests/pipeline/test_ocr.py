import pytest
from zerolan.data.pipeline.ocr import OCRQuery

from manager.config_manager import get_config
from pipeline.ocr.ocr_async import OCRAsyncPipeline
from pipeline.ocr.ocr_sync import OCRSyncPipeline

_config = get_config()
_ocr_async = OCRAsyncPipeline(_config.pipeline.ocr)
_ocr_sync = OCRSyncPipeline(_config.pipeline.ocr)


@pytest.fixture(scope="session")
def event_loop(event_loop_policy):
    # Needed to work with asyncpg
    loop = event_loop_policy.new_event_loop()
    yield loop
    loop.close()


def test_ocr_predict():
    query = OCRQuery(img_path="resources/ocr-test.png")
    prediction = _ocr_sync.predict(query)
    assert prediction, f"Test failed."
    print(prediction.model_dump_json())
    assert "我是赤川鹤鸣" in prediction.model_dump_json()


@pytest.mark.asyncio
async def test_ocr_predict():
    query = OCRQuery(img_path="resources/ocr-test.png")
    prediction = await _ocr_async.predict(query)
    assert prediction, f"Test failed: No response."
    print(prediction.model_dump_json())
    assert "我是赤川鹤鸣" in prediction.model_dump_json(), "Test failed: Wrong result."
