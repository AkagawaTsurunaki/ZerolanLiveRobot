import random
import re
from typing import List

from langchain_core.prompts import ChatPromptTemplate
from loguru import logger
from zerolan.data.data.ocr import RegionResult

from agent.adaptor import LangChainAdaptedLLM
from common.config import LLMPipelineConfig


def stringify(region_results: List[RegionResult]):
    result = ""
    for i, region_result in enumerate(region_results):
        line = f"[{i}] {region_result.content} \n"
        result += line
    return result


class LocationAttentionAgent:
    def __init__(self, config: LLMPipelineConfig):
        self._model: LangChainAdaptedLLM = LangChainAdaptedLLM(config=config)

    def find_focus(self, region_results: List[RegionResult]) -> RegionResult:
        system_template = "你的任务：你需要在下列的OCR识别结果中找到最具有值得注意的信息，最后返回其标号 [i]。"

        prompt_template = ChatPromptTemplate.from_messages(
            [("system", system_template), ("user", "{region_results}")]
        )

        result = prompt_template.invoke({"region_results": stringify(region_results)})
        result.to_messages()
        response = self._model.invoke(result)

        numbers = re.findall(r'\d+', response.content)

        if len(numbers) == 0:
            idx = random.randint(0, len(numbers) - 1)
        else:
            idx = int(numbers[0])

        logger.info(f"Location attention: [{idx}]{region_results[idx].content}")

        return region_results[idx]
