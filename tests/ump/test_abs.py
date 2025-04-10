import uuid

from zerolan.data.pipeline.llm import LLMQuery

from pipeline.synch.abs_pipeline import CommonModelPipeline, AbstractPipelineConfig, PipelineDisabledException

base_url = "http://127.0.0.1:5889"


class MyPipelineConfig(AbstractPipelineConfig):
    model_id: str = "test-llm-model"
    predict_url: str = f"{base_url}/llm/predict"
    stream_predict_url: str = f"{base_url}/llm/stream-predict"


def test_disabled_common_model_pipeline():
    cfg = MyPipelineConfig(
        enable=False,
        model_id="test-llm-model",
        predict_url=f"{base_url}/llm/predict",
        stream_predict_url=f"{base_url}/llm/stream-predict",
    )
    try:
        CommonModelPipeline(cfg)
    except Exception as e:
        assert isinstance(e, PipelineDisabledException), "Test passed"
    else:
        assert False, "Test failed"


def test_common_model_pipeline_predict():
    id = str(uuid.uuid4())

    p = CommonModelPipeline(MyPipelineConfig())
    r = p.predict(LLMQuery(id=id, text="Test", history=[]))
    # Common model pipeline will not auto convert AbstractModelPrediction to LLMPrediction
    assert id in r.model_dump_json()


def test_common_model_pipeline_stream_predict():
    id = str(uuid.uuid4())

    p = CommonModelPipeline(MyPipelineConfig())
    # Common model pipeline will not auto convert AbstractModelPrediction to LLMPrediction
    for r in p.stream_predict(LLMQuery(id=id, text="Test", history=[])):
        print(r)
