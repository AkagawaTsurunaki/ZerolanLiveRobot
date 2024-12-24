import asyncio
from typing import List

from loguru import logger
from zerolan.data.protocol.protocol import ZerolanProtocol

from common.data import PlaySpeechDTO, FileInfo, ScaleOperation, GameObjectInfo
from common.utils.audio_util import check_audio_format, check_audio_info
from common.utils.file_util import path_to_uri
from event.websocket import ZerolanProtocolWebsocket


class ZerolanViewerServer(ZerolanProtocolWebsocket):

    def __init__(self, host: str, port: int, protocol: str, version: str):
        super().__init__(host, port, protocol, version)
        self.gameobjects_info = {}

    def name(self):
        return "ZerolanViewerServer"

    async def on_protocol(self, protocol: ZerolanProtocol):
        logger.debug(protocol)
        if protocol.action == "client_hello":
            logger.debug("Client Hello")
            zp = ZerolanProtocol(protocol="ZerolanViewerProtocol", version="1.0", message="Server hello!", code=0,
                                 action="server_hello", data=None)
            await self._ws.send_json(zp.model_dump())
        elif protocol.action == "update_gameobjects_info":
            logger.debug("Update GameObjects Info")
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
                            duration=duration
                            )
        zp = ZerolanProtocol(protocol="ZerolanViewerProtocol", version="1.0",
                             message="Add the speech into a queue and waiting for playing", code=0,
                             action="play_speech", data=ana)
        await self._ws.send_json(zp.model_dump())
        logger.debug("Sent")

    async def load_model(self, file_info: FileInfo):
        zp = ZerolanProtocol(protocol="ZerolanViewerProtocol", version="1.0",
                             message="Load model from the specific file", code=0,
                             action="load_model", data=file_info)
        await self._ws.send_json(zp.model_dump())

    def get_gameobjects_info(self) -> List[GameObjectInfo]:
        result = []
        for k, v in self.gameobjects_info.items():
            result.append(v)
        return result

    async def modify_game_object_scale(self, operation: ScaleOperation):
        zp = ZerolanProtocol(protocol="ZerolanViewerProtocol", version="1.0",
                             message="Load model from the specific file", code=0,
                             action="modify_game_object_scale", data=operation)
        await self._ws.send_json(zp.model_dump())


async def run():
    server = ZerolanViewerServer(host="0.0.0.0", port=11013, protocol="ZerolanViewerProtocol", version="1.0")
    await server.start()


if __name__ == "__main__":
    asyncio.run(run())
