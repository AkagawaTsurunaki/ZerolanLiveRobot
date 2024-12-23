from typing import List

from langchain_core.prompts import ChatPromptTemplate

from agent.adaptor import LangChainAdaptedLLM
from common.config import get_config
from common.decorator import log_run_time


@log_run_time()
def find_file(files: List[dict], question: str) -> str | None:
    config = get_config()
    model = LangChainAdaptedLLM(config=config.pipeline.llm)

    system_template = '你现在是文件搜索助手，请根据用户的提问，寻找出最匹配的文件，并返回它的ID。注意：你只需要返回ID，不要输出任何其他内容'

    prompt_template = ChatPromptTemplate.from_messages(
        [("system", system_template), ("user",
                                       "{files} \n\n【你的任务】现在根据上述文件信息，和用户提问```\n{question}\n```\n寻找出最匹配的文件，并返回它的ID\n注意：你只需要返回ID，不要输出任何其他内容")]
    )

    result = prompt_template.invoke({"files": files, "question": question})
    result.to_messages()
    response = model.invoke(result)

    for file in files:
        if file["id"] in response.content:
            return file["id"]
    return None
