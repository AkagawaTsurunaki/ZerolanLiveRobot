from typing import List

from langchain_core.prompts import ChatPromptTemplate

from agent.adaptor import LangChainAdaptedLLM
from common.config import get_config
from common.data import GameObjectInfo, ScaleOperation
from common.decorator import log_run_time
from common.utils.json_util import smart_load_json_like


@log_run_time()
def model_scale(info: List[GameObjectInfo], question: str) -> ScaleOperation | None:
    config = get_config()
    model = LangChainAdaptedLLM(config=config.pipeline.llm)
    format = {
        "instance_id": int,
        "target_scale": float
    }

    system_template = '你现在需要根据用户的指令，修改游戏对象的一些参数。返回的JSON格式为{format}'
    user_template = '{info}【用户输入】{question}\n【你的任务】根据上面游戏对象的信息，识别用户需要操作的模型指令，将结果以JSON的形式返回。'

    prompt_template = ChatPromptTemplate.from_messages(
        [("system", system_template), ("user", user_template)]
    )

    result = prompt_template.invoke({"format": format, "info": info, "question": question})
    result.to_messages()
    response = model.invoke(result)
    json = smart_load_json_like(response.content)
    return ScaleOperation.model_validate(json)
