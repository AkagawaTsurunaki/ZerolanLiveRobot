import os.path

from loguru import logger
from zerolan.data.protocol.protocol import ZerolanProtocol

from common.config import PlaygroundBridgeConfig
from common.data import PlaySpeechDTO, LoadLive2DModelDTO, FileInfo, ScaleOperationDTO, CreateGameObjectDTO, \
    GameObjectInfo, ShowUserTextInputDTO, ServerHello
from common.enumerator import Action
from common.killable_thread import KillableThread
from common.utils.audio_util import check_audio_format, check_audio_info
from common.utils.collection_util import to_value_list
from common.utils.file_util import path_to_uri
from common.web.zrl_ws import ZerolanProtocolWsServer
from event.event_data import PlaygroundConnectedEvent, PlaygroundDisconnectedEvent
from event.eventemitter import emitter
from services.playground.grpc_server import GRPCServer


class PlaygroundBridge(ZerolanProtocolWsServer):

    def __init__(self, config: PlaygroundBridgeConfig):
        super().__init__(host=config.host, port=config.port)
        self.gameobjects_info = {}
        self._grpc_server = GRPCServer(config.grpc_server.host, config.grpc_server.port)
        self._grpc_server_thread: KillableThread | None = None

    def start(self):
        self._grpc_server_thread = KillableThread(target=self._grpc_server.start, daemon=True)
        self._grpc_server_thread.start()
        super().start()
        self._grpc_server_thread.join()

    def stop(self):
        super().stop()
        self._grpc_server_thread.kill()

    def name(self):
        return "PlaygroundBridge"

    def on_disconnect(self, ws_id: str):
        emitter.emit(PlaygroundDisconnectedEvent(ws_id=ws_id))

    def on_protocol(self, protocol: ZerolanProtocol):
        logger.info(f"{protocol.action}: {protocol.message}")
        if protocol.action == Action.CLIENT_HELLO:
            self._on_client_hello()
        elif protocol.action == Action.UPDATE_GAMEOBJECTS_INFO:
            self._on_update_gameobjects_info(protocol.data)

    def _on_client_hello(self):
        logger.info(f"ZerolanPlayground client is found, prepare for connecting...")
        grpc_server_url = f"http://{self._grpc_server.local_ip}:{self._grpc_server.port}"
        self.send(action=Action.SERVER_HELLO, data=ServerHello(grpc_server_url=grpc_server_url))
        emitter.emit(PlaygroundConnectedEvent())
        logger.info(f"`PlaygroundConnectedEvent` event emitted.")

    def _on_update_gameobjects_info(self, data: list[dict]):
        assert isinstance(data, list)
        self.gameobjects_info.clear()
        for info in data:
            go_info = GameObjectInfo.model_validate(info)
            self.gameobjects_info[go_info.instance_id] = go_info
        logger.debug("Local gameobjects cache is updated")

    def play_speech(self, bot_id: str, audio_path: str, transcript: str, bot_name: str):
        """
        Play a speech clip in the playground for specific bot with transcript subtitle.
        :param bot_id: The ID of the bot. You should configurate it in the `config.yaml`.
        :param audio_path: The speech file to be played.
        :param transcript: The transcript to be shown as subtitle.
        :return:
        """
        audio_type = check_audio_format(audio_path)
        sample_rate, num_channels, duration = check_audio_info(audio_path)
        audio_uri = path_to_uri(audio_path)
        self.send(action=Action.PLAY_SPEECH, data=PlaySpeechDTO(bot_id=bot_id, audio_uri=audio_uri,
                                                                bot_display_name=bot_name,
                                                                transcript=transcript,
                                                                audio_type=audio_type,
                                                                sample_rate=sample_rate,
                                                                channels=num_channels,
                                                                duration=duration))

    def load_live2d_model(self, dto: LoadLive2DModelDTO):
        """
        Load a specific Cubism Live2D model in the playground.
        :param dto: See LoadLive2DModelDTO
        """
        model_dir = dto.model_dir
        assert os.path.exists(model_dir) and os.path.isdir(model_dir), f"{model_dir} is not a directory"
        self.send(action=Action.LOAD_LIVE2D_MODEL, data=dto)

    def load_3d_model(self, file_info: FileInfo):
        """
        Load a specific 3D model as a GameObject in the playground.
        :param file_info: FileInfo
        """
        self.send(action=Action.LOAD_3D_MODEL,
                  data=file_info, message="Load 3D model")

    def modify_game_object_scale(self, dto: ScaleOperationDTO):
        """
        Modify the scale of a specific GameObject in the playground.
        :param dto: ScaleOperationDTO
        """
        self.send(action=Action.MODIFY_GAMEOBJECT_SCALE, data=dto)

    def create_gameobject(self, dto: CreateGameObjectDTO):
        """
        Create a built-in GameObject in the playground.
        :param dto: CreateGameObjectDTO
        :return:
        """
        self.send(action=Action.CREATE_GAMEOBJECT, data=dto)

    def query_update_gameobjects_info(self):
        """
        Make a query for updating the gameobjects info.
        This method does not make effects immediately.
        """
        self.send(action=Action.QUERY_GAMEOBJECTS_INFO, data=None)

    def get_gameobjects_info(self) -> list[GameObjectInfo]:
        """
        Get a list of the gameobjects info from the local cache.
        :return:
        """
        return to_value_list(self.gameobjects_info)

    def show_user_input_text(self, text: str):
        self.send(action=Action.SHOW_USER_TEXT_INPUT, data=ShowUserTextInputDTO(text=text))
