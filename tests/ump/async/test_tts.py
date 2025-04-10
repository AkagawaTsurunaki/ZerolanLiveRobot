import pytest
from zerolan.data.pipeline.tts import TTSQuery

from common.enumerator import Language
from pipeline.asynch.tts import TTSPipeline

_tts = TTSPipeline(base_url="http://127.0.0.1:11006", model_id="AkagawaTsurunaki/GPT-SoVITS")


@pytest.mark.asyncio
async def test_tts():
    query = TTSQuery(text="这是一段测试音频",
                     text_language=Language.ZH,
                     refer_wav_path="resources/[zh][Default]喜欢游戏的人和擅长游戏的人有很多不一样的地方，老师属于哪一种呢？.wav",
                     prompt_text="喜欢游戏的人和擅长游戏的人有很多不一样的地方，老师属于哪一种呢？",
                     prompt_language=Language.ZH)
    prediction = await _tts.predict(query=query)
    assert prediction and len(prediction.wave_data) > 0, "Test failed: No response."
    print(len(prediction.wave_data))


@pytest.mark.asyncio
async def test_stream_tts():
    query = TTSQuery(text="这是一段测试音频。如果你能听见我的话。那么说明测试成功了。这是一段流式音频。",
                     text_language=Language.ZH,
                     refer_wav_path="resources/[zh][Default]喜欢游戏的人和擅长游戏的人有很多不一样的地方，老师属于哪一种呢？.wav",
                     prompt_text="喜欢游戏的人和擅长游戏的人有很多不一样的地方，老师属于哪一种呢？",
                     prompt_language=Language.ZH)
    async for prediction in _tts.stream_predict(query=query):
        if prediction.is_final:
            break
        assert prediction and len(prediction.wave_data) > 0, "Test failed: No response."
        print(len(prediction.wave_data))
