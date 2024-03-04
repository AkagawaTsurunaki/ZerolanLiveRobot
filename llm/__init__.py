import os.path

from common import is_port_in_use, Code, HttpResponseBody
from llm.common import Config


def check_config(config: Config):
    """
    检查配置文件是否无误
    :param config:
    :return:
    """
    # 1. 检查 Port 是否被占用

    if is_port_in_use(config.port):
        return HttpResponseBody(
            code=Code.PORT_IS_ALREADY_USED,
            msg=f"以下端口正在被占用：{config.port}",
        )

    # 2. 检查 Tokenizer 路径

    if not os.path.exists(config.tokenizer_path):
        return HttpResponseBody(
            code=Code.PATH_DOSE_NOT_EXIST,
            msg=f"Tokenizer 路径不存在：{config.tokenizer_path}",
        )

    # 3. 检查 Model 路径
    if not os.path.exists(config.model_path):
        return HttpResponseBody(
            code=Code.PATH_DOSE_NOT_EXIST,
            msg=f"Model 路径不存在：{config.tokenizer_path}",
        )

    return HttpResponseBody(
        code=Code.OK,
        msg="LLM 服务配置成功"
    )


def start():
    """
    启动 ChatGLM3 服务。
    :return:
    """
    ...
    # 如果失败
    ...
    if ...:
        return HttpResponseBody(
            code=Code.ERROR,
            msg="LLM 服务启动失败"
        )
    # 如果成功
    return HttpResponseBody(
        code=Code.OK,
        msg="LMM 服务启动成功"
    )


def stop():
    """
    停止 ChatGLM3 服务。
    :return:
    """
    # 如果失败
    ...
    if ...:
        return HttpResponseBody(
            code=Code.ERROR,
            msg="LLM 服务停止失败"
        )
    # 如果成功
    return HttpResponseBody(
        code=Code.OK,
        msg="LMM 服务停止成功"
    )
