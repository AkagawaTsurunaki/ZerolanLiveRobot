from zerolan.data.pipeline.asr import ASRQuery
from zerolan.data.pipeline.img_cap import ImgCapQuery
from zerolan.data.pipeline.llm import LLMQuery
from zerolan.data.pipeline.ocr import OCRQuery
from zerolan.data.pipeline.tts import TTSStreamPrediction
from zerolan.data.pipeline.vla import ShowUiQuery, WebAction
from zerolan.ump.pipeline.asr import ASRPipeline
from zerolan.ump.pipeline.img_cap import ImgCapPipeline
from zerolan.ump.pipeline.ocr import OCRPipeline
from zerolan.ump.pipeline.vla import ShowUIPipeline

from common.config import get_config
from services.device.microphone import Microphone
from tests.shared import llm_predict_with_history, tts_stream_predict, create_pyaudio, close_pyaudio, tts_predict, \
    llm_pipeline

_config = get_config()

asr = ASRPipeline(_config.pipeline.asr)
imgcap = ImgCapPipeline(_config.pipeline.img_cap)
ocr = OCRPipeline(_config.pipeline.ocr)
showui = ShowUIPipeline(_config.pipeline.vla.showui)


def test_llm():
    query = LLMQuery(text="Hello world!", history=[])
    prediction = llm_pipeline.predict(query)
    assert prediction, f"No prediction from LLM pipeline."
    print(prediction.response)


def test_llm_history():
    prediction = llm_predict_with_history()
    print(prediction.response)


def test_tts():
    prediction = tts_predict("这是一段测试音频。是非流式的推理。意味着需要等待整段音频结束才能进行播放。")
    assert prediction, f"No prediction from TTS pipeline."
    assert prediction.wave_data is not None and len(
        prediction.wave_data) > 0, f"No audio data returned from TTS pipeline."


def test_tts2():
    p, stream = create_pyaudio()

    def handler(prediction: TTSStreamPrediction):
        stream.write(prediction.wave_data)  # 将音频数据写入音频流并播放

    tts_stream_predict(None, handler)
    # 自 TTS 发送 Post 到受到第一个请求的时延为 0.5s 左右，速度提升约3倍。
    close_pyaudio(p, stream)


def test_llm_tts_stream():
    llm_time_records: list[float] = []
    tts_time_records: list[float] = []

    for i in range(100):
        prediction = llm_predict_with_history(lambda elapsed_time: llm_time_records.append(elapsed_time))
        print(prediction.response)

        def handler(prediction: TTSStreamPrediction):
            print(prediction.seq)

        tts_stream_predict(prediction.response, handler,
                           lambda elapsed_time: tts_time_records.append(elapsed_time))

    i = 0
    print("No. LLM   TTS   Total")
    for llm_elapsed_time, tts_elapsed_time in zip(llm_time_records, tts_time_records):
        print(f"{i} {llm_elapsed_time:.4f} {tts_elapsed_time:.4f} {llm_elapsed_time + tts_elapsed_time:.4f}")
        i += 1

    print("----------------------")
    llm_avg = sum(llm_time_records) / len(llm_time_records)
    tts_avg = sum(tts_time_records) / len(tts_time_records)
    print(
        f"  {llm_avg:.4f} {tts_avg:.4f} {llm_avg + tts_avg:.4f} (avg)")
    print("Test passed.")

    # 基本可以将时延控制在 1.5s 左右
    # 在网络延时 100ms 的情况下，先进行 LLM 的非流式请求，然后进行 TTS 的流式请求
    # 多次实验的结果的平均值是
    # LLM 0.8891s，TTS 0.4369s，合计 1.3260s


def test_asr():
    microphone = Microphone()
    microphone.open()
    query = ASRQuery(audio_path="resources/tts-test.wav")
    prediction = asr.predict(query)
    assert prediction, f"No prediction from ASR pipeline."
    print(prediction.transcript)
    microphone.close()


def test_imgcap():
    query = ImgCapQuery(img_path="resources/imgcap-test.png")
    prediction = imgcap.predict(query)
    assert prediction, f"No prediction from ImgCap pipeline."
    print(prediction.caption)


def test_ocr():
    query = OCRQuery(img_path="resources/ocr-test.png")
    prediction = ocr.predict(query)
    assert prediction, f"No prediction from OCR pipeline."
    print(prediction.model_dump_json())


def test_showui():
    query = ShowUiQuery(img_path="resources/imgcap-test.png", query="Click the Ciallo")
    prediction = showui.predict(query)
    assert prediction.actions
    for action in prediction.actions:
        print(action.model_dump_json())

    query = ShowUiQuery(img_path="resources/imgcap-test.png", query="Click the Ciallo",
                        action=WebAction(action="CLICK"))
    prediction = showui.predict(query)
    assert prediction.actions
    for action in prediction.actions:
        print(action.model_dump_json())
    history = [WebAction(action="INPUT", value="Hello", position=None),
               WebAction(action="SELECT_TEXT", value=None, position=[0.2, 0.3])]
    query = ShowUiQuery(img_path="resources/imgcap-test.png", query="Click the Ciallo", env="web", history=history)
    prediction = showui.predict(query)
    assert prediction.actions
