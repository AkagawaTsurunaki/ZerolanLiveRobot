import time

from common.enumerator import Language
from tasks.llm_traslate_task import LLMTranslateTask
from tasks.ocr_summary_task import OcrSummaryTask


async def test_llm_translate_task():
    task = LLMTranslateTask(content="あなたの名前は？", from_lang=Language.JA, to_lang=Language.EN)
    ja_2_en = await task.run()
    print(ja_2_en)
    task = LLMTranslateTask(content="What is your name?", from_lang=Language.EN, to_lang=Language.ZH)
    en_2_zh = await task.run()
    print(en_2_zh)


async def test_ocr():
    time.sleep(3)
    task = OcrSummaryTask()
    ocr_sum = await task.run(win_title="Edge")
    print(ocr_sum)


if __name__ == '__main__':
    import asyncio

    asyncio.run(test_ocr())
