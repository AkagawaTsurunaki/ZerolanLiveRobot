import time
from typing import Callable

from zerolan.data.pipeline.asr import ASRQuery
from zerolan.data.pipeline.llm import LLMQuery, Conversation, RoleEnum
from zerolan.data.pipeline.tts import TTSStreamPrediction

from common.decorator import log_run_time
from common.utils.file_util import read_yaml
from pipeline.asr.sync.asr import ASRPipeline
from pipeline.synch.llm import LLMPipeline
from pipeline.config.config import LLMPipelineConfig
from pipeline.asr.config import ASRPipelineConfig
from ump.test_tts import tts_stream_predict

_config = read_yaml("./resources/config.test.yaml")
_llm = LLMPipeline(LLMPipelineConfig(
    model_id="",
    predict_url=_config['llm']['predict_url'],
    stream_predict_url=_config['llm']['stream_predict_url'])
)
_asr = ASRPipeline(ASRPipelineConfig(
    model_id=_config['asr']['model_id'],
    predict_url=_config['asr']['predict_url'],
    stream_predict_url=_config['asr']['stream_predict_url'],
))


def llm_predict_with_history(timer_handler: Callable[[float], None] | None = None):
    query = LLMQuery(text="你现在能和我玩游戏吗？",
                     history=[Conversation(role=RoleEnum.user, content="你现在是一只猫娘，请在句尾始终带上喵"),
                              Conversation(role=RoleEnum.assistant, content="好的，主人喵")])

    @log_run_time()
    def completed_llm_predict():
        t_start_post = time.time()
        prediction = _llm.predict(query)
        t_end_post = time.time()
        timer_handler(t_end_post - t_start_post)
        return prediction

    prediction = completed_llm_predict()
    return prediction


def asr_predict(timer_handler: Callable[[float], None] | None = None):
    query = ASRQuery(audio_path="/home/akagawatsurunaki/workspace/ZerolanLiveRobot/tests/resources/tts-test.wav",
                     channels=2)
    t_start_post = time.time()
    prediction = _asr.predict(query)
    t_end_post = time.time()
    if timer_handler is not None:
        timer_handler(t_end_post - t_start_post)
    return prediction


def test_llm_tts_stream():
    asr_time_records: list[float] = []
    llm_time_records: list[float] = []
    tts_time_records: list[float] = []

    for i in range(100):
        prediction = asr_predict(lambda elapsed_time: asr_time_records.append(elapsed_time))
        print(prediction.transcript)

        prediction = llm_predict_with_history(lambda elapsed_time: llm_time_records.append(elapsed_time))
        print(prediction.response)

        def handler(prediction: TTSStreamPrediction):
            print(prediction.seq)

        tts_stream_predict(prediction.response, handler,
                           lambda elapsed_time: tts_time_records.append(elapsed_time))

    i = 0
    print("No.,ASR,LLM,TTS,Total")
    for asr_elapsed_time, llm_elapsed_time, tts_elapsed_time in zip(asr_time_records, llm_time_records,
                                                                    tts_time_records):
        total = asr_elapsed_time + llm_elapsed_time + tts_elapsed_time
        print(f"{i} {asr_elapsed_time:4f} {llm_elapsed_time:.4f} {tts_elapsed_time:.4f} {total:.4f}")
        i += 1

    print("----------------------")
    asr_avg = sum(asr_time_records) / len(asr_time_records)
    llm_avg = sum(llm_time_records) / len(llm_time_records)
    tts_avg = sum(tts_time_records) / len(tts_time_records)
    print(
        f" {asr_avg:4f} {llm_avg:.4f} {tts_avg:.4f} {asr_avg + llm_avg + tts_avg:.4f} (avg)")
    print("Test passed.")

    # Basically, the latency can be controlled to about 1.5s
    # Non-streaming requests for LLMs are made first, followed by streaming requests for TTS
    # The average of the results of multiple experiments is:
    # LLM 0.8891s, TTS 0.4369s, Total 1.3260s (Win -> Ubuntu)
    # LLM 0.6507s, TTS 0.1542s, Total 0.8049s (Ubuntu -> Ubuntu)
