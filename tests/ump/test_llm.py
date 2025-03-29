from zerolan.data.pipeline.llm import LLMQuery, Conversation, RoleEnum

from common.utils.file_util import read_yaml
from ump.pipeline.llm import LLMPipeline
from ump.config import LLMPipelineConfig

_config = read_yaml("./resources/config.test.yaml")
_llm = LLMPipeline(LLMPipelineConfig(
    model_id="",
    predict_url=_config['llm']['predict_url'],
    stream_predict_url=_config['llm']['stream_predict_url'])
)


def _test_history(llm: LLMPipeline):
    query = LLMQuery(text="刚才我让你记住的名字是什么？", history=[
        Conversation(role=RoleEnum.user, content="请记住这个名字“赤川鹤鸣”"),
        Conversation(role=RoleEnum.assistant, content="好的，我会记住“赤川鹤鸣”这个名字")
    ])
    prediction = llm.predict(query)
    assert prediction, f"测试失败：管线返回了 None"
    print(prediction.response)
    assert "赤川鹤鸣" in prediction.response


def test_llm():
    query = LLMQuery(text="你好，你叫什么名字？", history=[])
    prediction = _llm.predict(query)
    assert prediction, f"测试失败：管线返回了 None"
    print(prediction.response)


def test_llm_with_history():
    _test_history(_llm)


def test_kimi_api():
    kimi_config = LLMPipelineConfig(model_id="moonshot-v1-8k",
                                    predict_url="https://api.moonshot.cn/v1",
                                    stream_predict_url="https://api.moonshot.cn/v1",
                                    api_key=_config['llm']['kimi_api_key'],
                                    openai_format=True)
    kimi = LLMPipeline(kimi_config)
    _test_history(kimi)


def test_deepseek_api():
    deepseek_config = LLMPipelineConfig(model_id="deepseek-chat",
                                        predict_url="https://api.deepseek.com",
                                        stream_predict_url="https://api.deepseek.com",
                                        api_key=_config['llm']['deepseek_api_key'],
                                        openai_format=True)
    deepseek = LLMPipeline(deepseek_config)
    _test_history(deepseek)
