from agent.summary import TextSummaryAgent
from common.config import get_config

_config = get_config()


def test_summary():
    with open("./resources/text.txt", mode="r", encoding="utf-8") as f:
        text = f.read()
    print(text)
    agent = TextSummaryAgent(_config.pipeline.llm)
    summary_text = agent.summary(text, 100)
    print(summary_text.content)
