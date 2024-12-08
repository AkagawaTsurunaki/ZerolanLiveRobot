from zerolan.data.pipeline.llm import Conversation, RoleEnum

from agent.summary import TextSummaryAgent
from common.config import get_config

_config = get_config()
_agent = TextSummaryAgent(_config.pipeline.llm)


def test_summary():
    with open("./resources/text.txt", mode="r", encoding="utf-8") as f:
        text = f.read()
    print(text)

    summary_text = _agent.summary(text, 100)
    print(summary_text.content)


def test_summary_history():
    history = [
        Conversation(role=RoleEnum.user, content="我最喜欢吃的东西是阿米糯司，你喜欢吃吗？"),
        Conversation(role=RoleEnum.assistant, content="阿米糯司？那是什么东西啊？听起来是一个寿司的名称……"),
        Conversation(role=RoleEnum.user, content="差不多吧。它是一种用糯米制作的东西，可好吃了。"),
        Conversation(role=RoleEnum.assistant, content="真的吗？那我下次也要尝尝阿米糯司！")
    ]
    summary_history = _agent.summary_history(history)
    print(summary_history.content)
