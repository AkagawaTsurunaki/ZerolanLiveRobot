import random
import re

from loguru import logger

from services.llm.pipeline import LLMPipeline, LLMQuery
from services.ocr.pipeline import OcrPipeline, OCRQuery, OCRPrediction
from tasks.llm.prompt import ICIOPrompt


class LLM_OCRLocationTask:
    def __init__(self, llm_pipeline: LLMPipeline = None, ocr_pipeline: OcrPipeline = None):
        self._llm_pipeline: LLMPipeline = LLMPipeline() if llm_pipeline is None else llm_pipeline
        self._ocr_pipeline: OcrPipeline = OcrPipeline() if ocr_pipeline is None else ocr_pipeline
        self._history = []

    async def run(self, img_path: str) -> tuple[OCRPrediction | None, int]:
        ocr_prediction = self._ocr_pipeline.predict(OCRQuery(img_path=img_path))

        input_data = ""
        for idx, region_result in enumerate(ocr_prediction.region_results):
            input_data += f"[{idx}]" + region_result.content + "\n"

        sys_prompt = ICIOPrompt(
            instruction=f"你需要在下列的OCR识别结果中找到最具有值得注意的信息，最后返回其标号 [i]。",
            input_data=input_data,
            output_indicator=f"必须仅返回标号，不要输出其他内容。"
        )
        query = LLMQuery(text=sys_prompt.en_format(), history=[])
        prediction = self._llm_pipeline.predict(query)

        numbers = re.findall(r'\d+', prediction.response)
        self._history = prediction.history

        if len(numbers) == 0:
            ret = random.randint(0, len(numbers) - 1)
        else:
            ret = int(numbers[0])

        logger.info(f"LLM-OCR 注意力定位任务结果: \n[{ret}]{ocr_prediction.region_results[ret].content}")

        return ocr_prediction, ret
