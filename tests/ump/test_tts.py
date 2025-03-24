import time
from typing import Callable

import pyaudio
from zerolan.data.pipeline.tts import TTSQuery, TTSStreamPrediction

from common.decorator import log_run_time
from common.enumerator import Language
from common.utils.file_util import read_yaml
from ump.pipeline.tts import TTSPipeline, TTSPipelineConfig

_config = read_yaml("./resources/config.test.yaml")
tts_pipeline = TTSPipeline(TTSPipelineConfig(
    model_id=_config['tts']['model_id'],
    predict_url=_config['tts']['predict_url'],
    stream_predict_url=_config['tts']['stream_predict_url'],
))


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


def tts_stream_predict(text: str | None, handler: Callable[[TTSStreamPrediction], None] | None,
                       timer_handler: Callable[[float], None] | None = None):
    text = text if text is not None else "这是一段随机生成的文字内容！我要喵喵叫！你听见了嘛？主人？"
    _tts_query.text = text

    @log_run_time()
    def completed_tts_stream_predict():
        first_rcv = False
        t_start_post = time.time()
        print(f"Start post: {t_start_post}")

        for prediction in tts_pipeline.stream_predict(_tts_query):
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


def tts_predict(text: str | None):
    text = text if text is not None else "这是一段随机生成的文字内容！我要喵喵叫！你听见了嘛？主人？"
    _tts_query.text = text

    @log_run_time()
    def predict():
        return tts_pipeline.predict(_tts_query)

    return predict()


def test_tts():
    prediction = tts_predict("这是一段测试音频。是非流式的推理。意味着需要等待整段音频结束才能进行播放。")
    assert prediction, f"No prediction from TTS pipeline."
    assert prediction.wave_data is not None and len(
        prediction.wave_data) > 0, f"No audio data returned from TTS pipeline."


# Warning: Running this test case will call the speaker,
#          you may hear a girl's voice, don't be afraid!
#          Take care to control your volume.
#          What you will hear is: 这是一段随机生成的文字内容！我要喵喵叫！你听见了嘛？主人？
def test_tts_with_sound_feedback():
    p, stream = create_pyaudio()

    def handler(prediction: TTSStreamPrediction):
        stream.write(prediction.wave_data)

    tts_stream_predict(None, handler)
    # The delay from sending a Post to receiving the first request is about 0.5s, which is about 3 times faster.
    close_pyaudio(p, stream)
