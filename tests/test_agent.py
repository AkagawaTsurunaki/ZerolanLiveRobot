import asyncio
from asyncio import TaskGroup

from zerolan.data.pipeline.llm import Conversation, RoleEnum

from agent.custom_agent import CustomAgent
from agent.model_modifier import model_scale
from agent.summary import TextSummaryAgent
from common.config import get_config
from common.data import GameObjectInfo
from services.viewer.app import ZerolanViewerServer

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


def test_model_scale():
    go_info_json = [{
        "instance_id": 42,
        "game_object_name": "白子",
        "transform": {
            "scale": 1,
            "position": {
                "x": 15.3,
                "y": -3.7,
                "z": 42.1
            }
        }
    }, {
        "instance_id": 1526,
        "game_object_name": "优香",
        "transform": {
            "scale": 1,
            "position": {
                "x": 5.3,
                "y": -3.7,
                "z": 2.1
            }
        }
    }]

    go_info = []
    for info in go_info_json:
        go_info.append(GameObjectInfo.model_validate(info))

    result = model_scale(go_info, "帮我放大一下优香")
    print(f"{result.instance_id}: {result.target_scale}")


async def atest_custom_agent():
    viewer = ZerolanViewerServer(host="0.0.0.0", port=11013, protocol="ZerolanViewerProtocol", version="1.0")
    async with TaskGroup() as tg:
        tg.create_task(viewer.start())
        await asyncio.sleep(5)
        agent = CustomAgent(_config.pipeline.llm, viewer)
        agent.run("创建一个绿色的立方体")


def test_custom_agent():
    asyncio.run(atest_custom_agent())
