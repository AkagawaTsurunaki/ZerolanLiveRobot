from zerolan.data.data.llm import LLMQuery
from zerolan.data.data.tts import TTSQuery

from common.config import get_config
from manager.tts_prompt_manager import TTSPromptManager
from pipeline.llm import LLMPipeline
from pipeline.tts import TTSPipeline

config = get_config()

llm = LLMPipeline(config.pipeline.llm)
tts = TTSPipeline(config.pipeline.tts)


def test_tts_prompt_manager():
    manager = TTSPromptManager(config=config.character.speech)
    assert len(manager.tts_prompts) > 0, f"{manager.tts_prompts} should not be empty."


def test_llm():
    query = LLMQuery(text="Hello world!", history=[])
    prediction = llm.predict(query)
    assert prediction, f"No prediction from LLM pipeline."


def test_tts():
    # Remember to change these variables
    refer_wav_path = ""
    prompt_text = ""
    prompt_language = ""
    query = TTSQuery(text="你好！能听见我说话吗？",
                     text_language="zh",
                     refer_wav_path=refer_wav_path,
                     prompt_text=prompt_text,
                     prompt_language=prompt_language)
    prediction = tts.predict(query)
    assert prediction, f"No prediction from TTS pipeline."


def test_asr():
    ...
