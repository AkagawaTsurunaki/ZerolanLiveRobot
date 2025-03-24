from zerolan.data.pipeline.ocr import OCRQuery

from common.utils.file_util import read_yaml
from ump.pipeline.ocr import OCRPipeline, OCRPipelineConfig

_config = read_yaml("./resources/config.test.yaml")
_ocr = OCRPipeline(OCRPipelineConfig(
    model_id=_config['ocr']['model_id'],
    predict_url=_config['ocr']['predict_url'],
    stream_predict_url=_config['ocr']['stream_predict_url'],
))


def test_ocr_predict():
    query = OCRQuery(img_path="resources/ocr-test.png")
    prediction = _ocr.predict(query)
    assert prediction, f"Test failed."
    print(prediction.model_dump_json())
    assert "我是赤川鹤鸣" in prediction.model_dump_json()
