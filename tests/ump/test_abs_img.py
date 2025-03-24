import uuid

from zerolan.data.pipeline.abs_data import AbsractImageModelQuery

from ump.abs_pipeline import AbstractPipelineConfig, AbstractImagePipeline

base_url = "http://127.0.0.1:5889"


class MyPipelineConfig(AbstractPipelineConfig):
    model_id: str = "test-llm-model"
    predict_url: str = f"{base_url}/abs-img/predict"
    stream_predict_url: str = f"{base_url}/abs-img/stream-predict"


def test_abs_img_pipeline_predict():
    id = str(uuid.uuid4())
    p = AbstractImagePipeline(MyPipelineConfig())
    r = p.predict(AbsractImageModelQuery(id=id, img_path="resources/imgcap-test.png"))
    assert r.id == id, "Test failed."


def test_abs_img_pipeline_stream_predict():
    id = str(uuid.uuid4())
    p = AbstractImagePipeline(MyPipelineConfig())
    for r in p.stream_predict(AbsractImageModelQuery(id=id, img_path="resources/imgcap-test.png")):
        assert r.id == id, "Test failed."
