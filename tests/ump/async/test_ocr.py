import pytest
from zerolan.data.pipeline.ocr import OCRQuery

from ump.asyncio.pipeline.ocr import OCRPipeline

_ocr = OCRPipeline(model_id="paddlepaddle/PaddleOCR", base_url='http://127.0.0.1:11004')


@pytest.mark.asyncio
async def test_ocr_predict():
    query = OCRQuery(img_path="resources/ocr-test.png")
    prediction = await _ocr.predict(query)
    assert prediction, f"Test failed: No response."
    print(prediction.model_dump_json())
    assert "我是赤川鹤鸣" in prediction.model_dump_json(), "Test failed: Wrong result."
