import asyncio
import os.path

from loguru import logger
from pydantic import BaseModel
from zerolan.data.protocol.protocol import ZerolanProtocol

from common.utils.audio_util import check_audio_format
from event.websocket import ZerolanProtocolWebsocket


class PlaySpeechDTO(BaseModel):
    bot_id: str
    audio_uri: str
    transcript: str
    audio_type: str


def path_to_uri(path):
    path = os.path.abspath(path)
    path = path.replace('\\', '/')
    uri = f'file:///{path}'
    return uri


class ZerolanViewerServer(ZerolanProtocolWebsocket):
    def name(self):
        return "ZerolanViewerServer"

    async def on_protocol(self, data: ZerolanProtocol):
        logger.debug(data)
        if data.action == "client_hello":
            logger.debug("Client Hello")
            zp = ZerolanProtocol(protocol="ZerolanViewerProtocol", version="1.0", message="Server hello!", code=0,
                                 action="server_hello", data=None)
            await self._ws.send_json(zp.model_dump())
            logger.debug("Sent")
            # elif data.action == "server_hello":
            audio_path = R"D:\AkagawaTsurunaki\WorkSpace\PythonProjects\ZerolanLiveRobot\resources\static\prompts\tts\[zh][Default]喜欢游戏的人和擅长游戏的人有很多不一样的地方，老师属于哪一种呢？.wav"
            audio_type = check_audio_format(audio_path)
            audio_uri = path_to_uri(audio_path)
            ana = PlaySpeechDTO(bot_id="UnityChan", audio_uri=audio_uri,
                                transcript="喜欢游戏的人和擅长游戏的人有很多不一样的地方，老师属于哪一种呢？",
                                audio_type=audio_type)
            zp = ZerolanProtocol(protocol="ZerolanViewerProtocol", version="1.0",
                                 message="Add the speech into a queue and waiting for playing", code=0,
                                 action="play_speech", data=ana)
            await self._ws.send_json(zp.model_dump())
            logger.debug("Sent")
        # if data.action == "add_audio":
        #     ...
        # else


async def run():
    server = ZerolanViewerServer(host="0.0.0.0", port=11013, protocol="ZerolanViewerProtocol", version="1.0")
    await server.start()


if __name__ == "__main__":
    asyncio.run(run())
