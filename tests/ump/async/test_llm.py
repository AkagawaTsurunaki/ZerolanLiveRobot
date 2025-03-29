import pytest
from zerolan.data.pipeline.llm import LLMQuery, Conversation, RoleEnum

from ump.asyncio.pipeline.llm import LLMPipeline

base_url = ""
_llm = LLMPipeline(model_id="glm4", base_url=base_url)


@pytest.mark.asyncio
async def test_llm():
    query = LLMQuery(text="Hello! What is your name?", history=[])
    prediction = await _llm.predict(query)
    print(prediction.model_dump_json(indent=4))
    assert prediction and prediction.response, f"Test failed: No response."


@pytest.mark.asyncio
async def test_llm_history():
    query = LLMQuery(text="Now please tell me the name I told you to remember.", history=[
        Conversation(role=RoleEnum.user, content="Please remember this name: AkagawaTsurunaki"),
        Conversation(role=RoleEnum.assistant, content="Ok. I remembered your name AkagawaTsurunaki")
    ])
    prediction = await _llm.predict(query)
    print(prediction.model_dump_json(indent=4))
    assert prediction and prediction.response, f"Test failed: No response."
    assert "Akagawa" in prediction.response, f"Test failed: History may be not injected."


@pytest.mark.asyncio
async def test_llm_stream_predict():
    query = LLMQuery(text="Hello! What is your name?", history=[])
    prediction = await _llm.predict(query)
    print(prediction.model_dump_json(indent=4))
    assert prediction and prediction.response, f"Test failed: No response."
