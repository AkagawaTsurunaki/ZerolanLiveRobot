from loguru import logger
from zerolan.data.protocol.protocol import ZerolanProtocol

from common.data import GameObjectInfo
from event.websocket import ZerolanProtocolWebsocket
from services.playground.api import Action, send


class PlaygroundBridge(ZerolanProtocolWebsocket):

    def __init__(self, host: str, port: int):
        super().__init__(host, port)
        self.gameobjects_info = {}

    async def on_protocol(self, protocol: ZerolanProtocol):
        logger.info(f"{protocol.action}: {protocol.message}")
        if protocol.action == Action.CLIENT_HELLO:
            await self._on_client_hello()
        elif protocol.action == Action.UPDATE_GAMEOBJECTS_INFO:
            self._on_update_gameobjects_info(protocol.data)

    def name(self):
        return "PlaygroundBridge"

    async def _on_client_hello(self):
        logger.info(f"ZerolanPlayground 客户端发现，准备建立连接")
        await send(action=Action.SERVER_HELLO, data=None)

    def _on_update_gameobjects_info(self, data: list[dict]):
        assert isinstance(data, list)
        self.gameobjects_info.clear()
        for info in data:
            go_info = GameObjectInfo.model_validate(info)
            self.gameobjects_info[go_info.instance_id] = go_info
        logger.debug("本地游戏对象缓存已更新")
