import asyncio
from typing import List

from loguru import logger
from zerolan.data.protocol.protocol import ZerolanProtocol

from common.data import PlaySpeechDTO, FileInfo, ScaleOperation, GameObjectInfo, ViewerAction
from common.utils.audio_util import check_audio_format, check_audio_info
from common.utils.file_util import path_to_uri
from event.websocket import ZerolanProtocolWebsocket


class ZerolanViewerServer(ZerolanProtocolWebsocket):

    def __init__(self, host: str, port: int, protocol: str, version: str):
        super().__init__(host, port, protocol, version)
        self.gameobjects_info = {}

    def name(self):
        return "ZerolanViewerServer"

    @staticmethod
    def _create_protocol(message: str, action: ViewerAction, data: any, code: int = 0):
        zp = ZerolanProtocol(protocol="ZerolanViewerProtocol", version="1.0",
                             message=message, code=code,
                             action=action.value, data=data)
        return zp

    async def on_protocol(self, protocol: ZerolanProtocol):
        logger.info(f"{protocol.action}: {protocol.message}")
        if protocol.action == ViewerAction.CLIENT_HELLO:
            zp = ZerolanProtocol(protocol="ZerolanViewerProtocol", version="1.0", message="Server hello!", code=0,
                                 action="server_hello", data=None)
            await self._ws.send_json(zp.model_dump())
        elif protocol.action == ViewerAction.UPDATE_GAMEOBJECTS_INFO:
            assert isinstance(protocol.data, list)
            for info in protocol.data:
                go_info = GameObjectInfo.model_validate(info)
                self.gameobjects_info[go_info.instance_id] = go_info

    async def play_speech(self, bot_id: str, audio_path: str, transcript: str):
        audio_type = check_audio_format(audio_path)
        sample_rate, num_channels, duration = check_audio_info(audio_path)
        audio_uri = path_to_uri(audio_path)
        ana = PlaySpeechDTO(bot_id=bot_id, audio_uri=audio_uri,
                            transcript=transcript,
                            audio_type=audio_type,
                            sample_rate=sample_rate,
                            channels=num_channels,
                            duration=duration)
        zp = self._create_protocol(message="Add the speech into a queue and waiting for playing",
                                   action=ViewerAction.PLAY_SPEECH,
                                   data=ana)
        await self._ws.send_json(zp.model_dump())
        logger.debug("Sent")

    async def load_model(self, file_info: FileInfo):
        zp = self._create_protocol(message="Load model from the specific file",
                                   action=ViewerAction.LOAD_MODEL,
                                   data=file_info)
        await self._ws.send_json(zp.model_dump())

    def get_gameobjects_info(self) -> List[GameObjectInfo]:
        result = []
        for k, v in self.gameobjects_info.items():
            result.append(v)
        return result

    async def modify_game_object_scale(self, operation: ScaleOperation):
        zp = self._create_protocol(message="Modify the game object scale",
                                   action=ViewerAction.MODIFY_GAME_OBJECT_SCALE,
                                   data=operation)
        await self._ws.send_json(zp.model_dump())


async def run():
    server = ZerolanViewerServer(host="0.0.0.0", port=11013, protocol="ZerolanViewerProtocol", version="1.0")
    await server.start()


if __name__ == "__main__":
    asyncio.run(run())
