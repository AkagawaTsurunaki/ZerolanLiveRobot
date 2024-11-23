from zerolan.data.pipeline.asr import ASRQuery
from zerolan.data.pipeline.img_cap import ImgCapQuery
from zerolan.data.pipeline.llm import LLMQuery
from zerolan.data.pipeline.ocr import OCRQuery
from zerolan.data.pipeline.tts import TTSQuery

from common.config import get_config
from manager.tts_prompt_manager import TTSPromptManager
from pipeline.asr import ASRPipeline
from pipeline.img_cap import ImgCapPipeline
from pipeline.llm import LLMPipeline
from pipeline.ocr import OCRPipeline
from pipeline.tts import TTSPipeline
from services.device.microphone import Microphone

config = get_config()

llm = LLMPipeline(config.pipeline.llm)
tts = TTSPipeline(config.pipeline.tts)
asr = ASRPipeline(config.pipeline.asr)
imgcap = ImgCapPipeline(config.pipeline.img_cap)
ocr = OCRPipeline(config.pipeline.ocr)

manager = TTSPromptManager(config=config.character.speech)
assert len(manager.tts_prompts) > 0, f"{manager.tts_prompts} should not be empty."
prompt = manager.tts_prompts[0]


def test_llm():
    query = LLMQuery(text="Hello world!", history=[])
    prediction = llm.predict(query)
    assert prediction, f"No prediction from LLM pipeline."


def test_tts():
    query = TTSQuery(text="你好！能听见我说话吗？",
                     text_language="zh",
                     refer_wav_path=prompt.audio_path,
                     prompt_text=prompt.prompt_text,
                     prompt_language=prompt.lang)
    prediction = tts.predict(query)
    assert prediction, f"No prediction from TTS pipeline."
    assert prediction.wave_data is not None and len(
        prediction.wave_data) > 0, f"No audio data returned from TTS pipeline."


def test_asr():
    microphone = Microphone()
    microphone.open()
    query = ASRQuery(audio_path=prompt.audio_path)
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