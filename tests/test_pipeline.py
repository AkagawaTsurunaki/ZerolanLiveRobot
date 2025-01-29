from zerolan.data.pipeline.asr import ASRQuery
from zerolan.data.pipeline.img_cap import ImgCapQuery
from zerolan.data.pipeline.llm import LLMQuery, Conversation, RoleEnum
from zerolan.data.pipeline.ocr import OCRQuery
from zerolan.data.pipeline.tts import TTSQuery
from zerolan.data.pipeline.vla import ShowUiQuery, WebAction

from common.config import get_config
from common.enumerator import Language
from zerolan.ump.pipeline.asr import ASRPipeline
from zerolan.ump.pipeline.img_cap import ImgCapPipeline
from zerolan.ump.pipeline.llm import LLMPipeline
from zerolan.ump.pipeline.ocr import OCRPipeline
from zerolan.ump.pipeline.tts import TTSPipeline
from zerolan.ump.pipeline.vla import ShowUIPipeline
from services.device.microphone import Microphone

_config = get_config()

llm = LLMPipeline(_config.pipeline.llm)
tts = TTSPipeline(_config.pipeline.tts)
asr = ASRPipeline(_config.pipeline.asr)
imgcap = ImgCapPipeline(_config.pipeline.img_cap)
ocr = OCRPipeline(_config.pipeline.ocr)
showui = ShowUIPipeline(_config.pipeline.vla.showui)


def test_llm():
    query = LLMQuery(text="Hello world!", history=[])
    prediction = llm.predict(query)
    assert prediction, f"No prediction from LLM pipeline."
    print(prediction.response)


def test_llm_history():
    query = LLMQuery(text="你现在能和我玩游戏吗？",
                     history=[Conversation(role=RoleEnum.user, content="你现在是一只猫娘，请在句尾始终带上喵"),
                              Conversation(role=RoleEnum.assistant, content="好的，主人喵")])
    prediction = llm.predict(query)
    assert prediction, f"No prediction from LLM pipeline."
    print(prediction.response)


def test_tts():
    query = TTSQuery(text="你好！能听见我说话吗？",
                     text_language=Language.ZH,
                     refer_wav_path="resources/tts-test.wav",
                     prompt_text="我是赤川鹤鸣",
                     prompt_language=Language.ZH)
    prediction = tts.predict(query)
    assert prediction, f"No prediction from TTS pipeline."
    assert prediction.wave_data is not None and len(
        prediction.wave_data) > 0, f"No audio data returned from TTS pipeline."


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
