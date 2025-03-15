import time
from typing import Callable

import pyaudio
from zerolan.data.pipeline.asr import ASRQuery
from zerolan.data.pipeline.llm import LLMQuery, Conversation, RoleEnum
from zerolan.data.pipeline.tts import TTSQuery, TTSStreamPrediction
from zerolan.ump.pipeline.asr import ASRPipeline
from zerolan.ump.pipeline.img_cap import ImgCapPipeline
from zerolan.ump.pipeline.llm import LLMPipeline
from zerolan.ump.pipeline.ocr import OCRPipeline
from zerolan.ump.pipeline.tts import TTSPipeline
from zerolan.ump.pipeline.vla import ShowUIPipeline

from common.config import get_config
from common.decorator import log_run_time
from common.enumerator import Language

_config = get_config()

llm_pipeline = LLMPipeline(_config.pipeline.llm)
tts_pipeline = TTSPipeline(_config.pipeline.tts)
asr_pipeline = ASRPipeline(_config.pipeline.asr)
imgcap_pipeline = ImgCapPipeline(_config.pipeline.img_cap)
ocr_pipeline = OCRPipeline(_config.pipeline.ocr)
showui_pipeline = ShowUIPipeline(_config.pipeline.vla.showui)

_CHUNK_SIZE = 1024  # 每次处理的音频数据大小


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


def llm_predict_with_history(timer_handler: Callable[[float], None] | None = None):
    query = LLMQuery(text="你现在能和我玩游戏吗？",
                     history=[Conversation(role=RoleEnum.user, content="你现在是一只猫娘，请在句尾始终带上喵"),
                              Conversation(role=RoleEnum.assistant, content="好的，主人喵")])

    @log_run_time()
    def completed_llm_predict():
        t_start_post = time.time()
        prediction = llm_pipeline.predict(query)
        t_end_post = time.time()
        timer_handler(t_end_post - t_start_post)
        return prediction

    prediction = completed_llm_predict()
    return prediction


_tts_query = TTSQuery(text="",
                      text_language=Language.ZH,
                      refer_wav_path="/home/akagawatsurunaki/workspace/ZerolanLiveRobot/resources/static/prompts/tts/[zh][Default]喜欢游戏的人和擅长游戏的人有很多不一样的地方，老师属于哪一种呢？.wav",
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


def asr_predict(timer_handler: Callable[[float], None] | None = None):
    query = ASRQuery(audio_path="/home/akagawatsurunaki/workspace/ZerolanLiveRobot/tests/resources/tts-test.wav",
                     channels=2)
    t_start_post = time.time()
    prediction = asr_pipeline.predict(query)
    t_end_post = time.time()
    if timer_handler is not None:
        timer_handler(t_end_post - t_start_post)
    return prediction