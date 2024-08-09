from dataclasses import dataclass

import websockets
from dataclasses_json import dataclass_json
from loguru import logger
from retry import retry

from common.buffer.game_buf import MinecraftGameEventBuffer, MinecraftGameEvent
from common.config.service_config import ServiceConfig

config = ServiceConfig.game_config


@dataclass_json
@dataclass
class ZerolanLiveRobotWebsocketDto:
    protocol: str
    action: str
    message: str
    body: any


class Action:
    bot_damage = "botDamage"

    zh_dict = {
        bot_damage: "受伤"
    }


entity_type_zh_dict = {
    "player": "玩家",
    "mob": "生物",
    "object": "物品",
    "global": "全局",
    "orb": "经验球",
    "projectile": "投掷物",
    "hostile": "敌对生物",
    "other": "其他"
}

entity_display_name_zh_dict = {
    "Zombie": "僵尸"
}


class KonekoMinecraftAIAgent:

    def __init__(self):
        super().__init__()
        self.game_evt_buf: MinecraftGameEventBuffer = MinecraftGameEventBuffer()
        self._url = "ws://127.0.0.1:10056"

    @retry(exceptions=ConnectionRefusedError, tries=5)
    async def start(self):
        """
        此方法会阻塞主线程, 请使用新的线程以处理
        """
        async with websockets.connect(self._url) as websocket:
            while True:
                # 接收消息
                message = await websocket.recv()
                # 将消息转换为 JSON 对象
                dto: ZerolanLiveRobotWebsocketDto = ZerolanLiveRobotWebsocketDto.from_json(message)  # type: ignore
                # 打印 JSON 数据
                logger.info(dto)
                event = self.interpret(dto)
                if event is not None:
                    self.game_evt_buf.append(event)

    def interpret(self, dto: ZerolanLiveRobotWebsocketDto):
        if dto.action == Action.bot_damage:
            entity_type = dto.body.get("sourceCauseEntityType", None)
            if entity_type is not None:
                entity_type = entity_type_zh_dict.get(entity_type, None)

            display_name = dto.body.get("sourceCauseEntityDisplayName", None)
            if display_name is not None:
                display_name = entity_display_name_zh_dict.get(display_name, None)
            message = f"""
            你被{entity_type if entity_type is not None else ""}{display_name if display_name is not None else ""}攻击并受伤了
            """.strip()
            logger.debug(f"🧟 [{entity_type}]{display_name} => 🤖 ")
            return MinecraftGameEvent(event=Action.bot_damage,
                                      message=message,
                                      body=dto.body)
