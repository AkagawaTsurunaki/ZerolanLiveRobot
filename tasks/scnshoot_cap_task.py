from common.enum.lang import Language
from manager.device.screen import Screen
from services.img_cap.pipeline import ImgCapQuery
from pipeline.img_cap import ImaCapPipeline
from pipeline.llm import LLMPipeline
from tasks.llm.llm_traslate_task import LLMTranslateTask


class ScreenshotCaptionTask:
    """
    将屏幕截图存储到临时文件，并调用图像字幕模型，获取图像的文字描述内容。
    """
    def __init__(self, llm_pipeline: LLMPipeline = None, imgcap_pipeline: ImaCapPipeline = None):
        self._llm_translate_task: LLMTranslateTask = LLMTranslateTask(llm_pipeline)
        self._imgcap_pipeline: ImaCapPipeline = ImaCapPipeline() if imgcap_pipeline is None else imgcap_pipeline

    async def run(self, win_title: str, k: float):
        # 获取屏幕截图
        img, img_save_path = Screen.screen_cap(win_title, k)
        if img_save_path is not None:
            imgcap_query = ImgCapQuery(img_path=img_save_path, prompt="There")
            imgcap_prediction = self._imgcap_pipeline.predict(imgcap_query)
            if imgcap_prediction is not None:
                imgcap_zh = await self._llm_translate_task.run(content=imgcap_prediction.caption,
                                                               from_lang=Language.value_of(imgcap_prediction.lang),
                                                               to_lang=Language.ZH)
                return imgcap_zh
        return None
