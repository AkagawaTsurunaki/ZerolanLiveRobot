import pytest
from loguru import logger
from zerolan.data.pipeline.llm import LLMQuery, Conversation, RoleEnum

from manager.config_manager import get_config, get_project_dir
from pipeline.llm.config import LLMPipelineConfig
from pipeline.llm.llm_sync import LLMSyncPipeline
from pipeline.llm.llm_async import LLMAsyncPipeline

_config = get_config()
_llm_async = LLMAsyncPipeline(_config.pipeline.llm)
_llm_sync = LLMSyncPipeline(_config.pipeline.llm)
project_dir = get_project_dir()
_llm_query = LLMQuery(text="刚才我让你记住的名字是什么？", history=[
    Conversation(role=RoleEnum.user, content="请记住这个名字“赤川鹤鸣”"),
    Conversation(role=RoleEnum.assistant, content="好的，我会记住“赤川鹤鸣”这个名字")
])
_kimi_api_key = None
_dp_api_key = None


@pytest.fixture(scope="session")
def event_loop(event_loop_policy):
    # Needed to work with asyncpg
    loop = event_loop_policy.new_event_loop()
    yield loop
    loop.close()


@pytest.mark.asyncio
async def test_llm_async():
    query = LLMQuery(text="Hello! What is your name?", history=[])
    prediction = await _llm_async.predict(query)
    print(prediction.model_dump_json(indent=4))
    assert prediction and prediction.response, f"Test failed: No response."


@pytest.mark.asyncio
async def test_llm_history_async():
    query = LLMQuery(text="Now please tell me the name I told you to remember.", history=[
        Conversation(role=RoleEnum.user, content="Please remember this name: AkagawaTsurunaki"),
        Conversation(role=RoleEnum.assistant, content="Ok. I remembered your name AkagawaTsurunaki")
    ])
    prediction = await _llm_async.predict(query)
    logger.info(prediction.model_dump_json(indent=4))
    assert prediction and prediction.response, f"Test failed: No response."
    assert "Akagawa" in prediction.response, f"Test failed: History may be not injected."


@pytest.mark.asyncio
async def test_llm_stream_predict():
    query = LLMQuery(text="Hello! What is your name?", history=[])
    prediction = await _llm_async.predict(query)
    logger.info(prediction.model_dump_json(indent=4))
    assert prediction and prediction.response, f"Test failed: No response."


def test_llm():
    query = LLMQuery(text="你好，你叫什么名字？", history=[])
    prediction = _llm_sync.predict(query)
    assert prediction, f"Test failed: No response."
    logger.info(prediction.response)
    assert len(prediction.response) > 0, f"Test failed: No text response."


def _chat(llm_sync: LLMSyncPipeline):
    prediction = llm_sync.predict(_llm_query)
    assert prediction, f"Test failed: No response."
    logger.info(prediction.response)


def test_kimi_api():
    if not _kimi_api_key:
        logger.warning("No API key provided. Ignore this test case.")
        return
    kimi_config = LLMPipelineConfig(model_id="moonshot-v1-8k",
                                    predict_url="https://api.moonshot.cn/v1",
                                    stream_predict_url="https://api.moonshot.cn/v1",
                                    api_key=_kimi_api_key,
                                    openai_format=True)
    kimi = LLMSyncPipeline(kimi_config)
    _chat(kimi)


def test_deepseek_api():
    if not _dp_api_key:
        logger.warning("No API key provided. Ignore this test case.")
        return
    deepseek_config = LLMPipelineConfig(model_id="deepseek-chat",
                                        predict_url="https://api.deepseek.com",
                                        stream_predict_url="https://api.deepseek.com",
                                        api_key=_dp_api_key,
                                        openai_format=True)
    deepseek = LLMSyncPipeline(deepseek_config)
    _chat(deepseek)
