import copy

from loguru import logger

from services.device.screen import Screen
from pipeline.llm import LLMPipeline
from zerolan_live_robot_data.data.llm import LLMQuery
from zerolan_live_robot_data.data.ocr import OCRQuery
from pipeline.ocr import OcrPipeline
from tasks.llm.prompt import ICIOPrompt


class OcrSummaryTask:
    """
    获取指定窗口中的内容并总结
    """

    def __init__(self, llm_pipeline: LLMPipeline = None, ocr_pipeline: OcrPipeline = None):
        self._llm_pipeline: LLMPipeline = LLMPipeline() if llm_pipeline is None else llm_pipeline
        self._ocr_pipeline: OcrPipeline = OcrPipeline() if ocr_pipeline is None else ocr_pipeline

        self._sys_prompt: ICIOPrompt = ICIOPrompt(
            instruction=f"你将要对所给的 OCR 内容进行格式整理，注意保持文段整洁性，不要遗漏大量文字",
            context=None,
            input_data=None,
            output_indicator=None
        )

    async def run(self, win_title: str = "Firefox"):
        img, img_path = Screen.capture(win_title)
        ocr_p = self._ocr_pipeline.predict(OCRQuery(img_path))
        logger.info(f"OCR 结果：{ocr_p.unfold_as_str()}")
        sys_prompt = copy.deepcopy(self._sys_prompt)
        sys_prompt.input_data = ocr_p.unfold_as_str()
        query = LLMQuery(text=sys_prompt.en_format(), history=[])
        prediction = self._llm_pipeline.predict(query)
        logger.info(f"OCR 总结结果: {prediction.response}")
        return prediction.response
