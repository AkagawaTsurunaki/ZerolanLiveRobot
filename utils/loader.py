import json
import os

from loguru import logger

from chatglm3.api import ModelRequest
from controller import DEFAULT_CUSTOM_PROMPT_FILE_PATH


def load_llm_sys_prompt():
    """
    加载用户自定义的提示词模板。
    如果在默认路径 {DEFAULT_CUSTOM_PROMPT_FILE_PATH} 下找不到对应的文件，那么就会创建一个。
    :return: ModelRequest
    """

    # 如果用户没有设置自己的自定义提示词，那么自动使用默认提示词
    if not os.path.exists(DEFAULT_CUSTOM_PROMPT_FILE_PATH):
        with open(file=DEFAULT_CUSTOM_PROMPT_FILE_PATH, mode='w+', encoding='utf-8') as file:
            model_req = ModelRequest(sys_prompt='', query='', temperature=1., top_p=1., history=[])
            json.dump(obj=model_req, fp=file, ensure_ascii=False, indent=4)
            logger.warning(
                f'已生成用户自定义的提示词模板，您可以到以下路径进行具体内容修改：{DEFAULT_CUSTOM_PROMPT_FILE_PATH}')

    with open(file=DEFAULT_CUSTOM_PROMPT_FILE_PATH, mode='r', encoding='utf-8') as file:
        json_value = json.load(file)
        model_req = ModelRequest(**json_value)
    logger.info(f'LLM 提示词模板加载完毕')
    return model_req
