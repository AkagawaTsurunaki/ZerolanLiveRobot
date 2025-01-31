from injector import inject
from zerolan.data.protocol.protocol import ZerolanProtocol

from common.config import QQBotBridgeConfig
from event.event_data import QQMessageEvent
from event.eventemitter import emitter
from event.websocket import ZerolanProtocolWebsocket


class _QQBotAction:
    GROUP_MESSAGE = "group_message"


class QQBotBridge(ZerolanProtocolWebsocket):

    @inject
    def __init__(self, config: QQBotBridgeConfig):
        host, port = config.host, config.port
        ZerolanProtocolWebsocket.__init__(self, host=host, port=port)

    async def on_protocol(self, protocol: ZerolanProtocol):
        if protocol.action == _QQBotAction.GROUP_MESSAGE:
            msg = protocol.data["message"]
            group_id = protocol.data.get("group_id", None)
            emitter.emit(QQMessageEvent(message=msg, group_id=group_id))

    def name(self):
        return "QQBotBridge"

    async def send_plain_message(self, message: str, group: int):
        await self.send(action="send_plain_text_in_group", data={
            "group": group,
            "message": message
        })
