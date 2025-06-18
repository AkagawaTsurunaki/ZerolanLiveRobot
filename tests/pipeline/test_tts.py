import time
from copy import deepcopy
from typing import Callable

import pyaudio
import pytest
from zerolan.data.pipeline.tts import TTSQuery, TTSStreamPrediction

from common.decorator import log_run_time
from common.enumerator import Language
from common.io.api import save_audio
from common.io.file_type import AudioFileType
from manager.config_manager import get_config
from manager.tts_prompt_manager import TTSPromptManager
from pipeline.tts.tts_async import TTSAsyncPipeline
from pipeline.tts.tts_sync import TTSSyncPipeline

_config = get_config()
_tts = TTSAsyncPipeline(_config.pipeline.tts)


@pytest.fixture(scope="session")
def event_loop(event_loop_policy):
    # Needed to work with asyncpg
    loop = event_loop_policy.new_event_loop()
    yield loop
    loop.close()


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


_tts_sync = TTSSyncPipeline(_config.pipeline.tts)


def create_pyaudio():
    p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=32000,
                    output=True)
    return p, stream


def close_pyaudio(p, stream):
    stream.stop_stream()
    stream.close()
    p.terminate()


_tts_query = TTSQuery(text="",
                      text_language=Language.ZH,
                      refer_wav_path="resources/[zh][Default]喜欢游戏的人和擅长游戏的人有很多不一样的地方，老师属于哪一种呢？.wav",
                      prompt_text="喜欢游戏的人和擅长游戏的人有很多不一样的地方，老师属于哪一种呢？",
                      prompt_language=Language.ZH)

_tts_manager = TTSPromptManager(_config.character.speech)
_tts_manager.set_lang(Language.ZH)
_tts_prompt = _tts_manager.tts_prompts[0]
_tts_query.refer_wav_path = _tts_prompt.audio_path
_tts_query.prompt_text = _tts_prompt.prompt_text
_tts_query.prompt_language = _tts_prompt.lang


def tts_stream_predict(text: str | None, handler: Callable[[TTSStreamPrediction], None] | None,
                       timer_handler: Callable[[float], None] | None = None):
    text = text if text is not None else "这是一段随机生成的文字内容！我要喵喵叫！你听见了嘛？主人？"
    _tts_query.text = text

    @log_run_time()
    def completed_tts_stream_predict():
        first_rcv = False
        t_start_post = time.time()
        print(f"Start post: {t_start_post}")

        for prediction in _tts_sync.stream_predict(_tts_query):
            if not first_rcv:
                first_rcv = True
                t_first_chunk = time.time()
                print(f"Post data got: {time.time()}")
                print(f"Elapsed time: {t_first_chunk - t_start_post}")
                if timer_handler is not None:
                    timer_handler(t_first_chunk - t_start_post)
            if handler is not None:
                handler(prediction)

    return completed_tts_stream_predict()


def _tts_predict(text: str | None):
    text = text if text is not None else "这是一段随机生成的文字内容！我要喵喵叫！你听见了嘛？主人？"
    _tts_query.text = text

    @log_run_time()
    def predict():
        return _tts_sync.predict(_tts_query)

    return predict()


def test_tts_sync():
    q = deepcopy(_tts_query)
    q.text = "这是一段测试音频。是非流式的推理。意味着需要等待整段音频结束才能进行播放。"
    q.audio_type = 'wav'

    @log_run_time()
    def predict():
        return _tts_sync.predict(q)

    prediction = predict()
    assert prediction, f"No prediction from TTS pipeline."
    assert prediction.wave_data is not None and len(
        prediction.wave_data) > 0, f"No audio data returned from TTS pipeline."
    save_audio(prediction.wave_data, AudioFileType.WAV, "test-tts")


# Warning: Running this test case will call the speaker,
#          you may hear a girl's voice!
#          Take care to control your volume.
#          What you will hear is: 这是一段随机生成的文字内容！我要喵喵叫！你听见了嘛？主人？
def test_tts_with_sound_feedback():
    p, stream = create_pyaudio()

    def handler(prediction: TTSStreamPrediction):
        stream.write(prediction.wave_data)

    tts_stream_predict(None, handler)
    # The delay from sending a Post to receiving the first request is about 0.5s, which is about 3 times faster.
    close_pyaudio(p, stream)
