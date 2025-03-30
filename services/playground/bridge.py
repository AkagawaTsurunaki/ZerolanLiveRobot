import os.path
import uuid
from enum import Enum
from typing import List

from loguru import logger
from typeguard import typechecked
from zerolan.data.protocol.protocol import ZerolanProtocol

from common.config import get_config
from common.utils.audio_util import check_audio_format, check_audio_info
from common.utils.collection_util import to_value_list
from common.utils.file_util import create_temp_file, compress_directory
from common.utils.web_util import get_local_ip
from common.web.zrl_ws import ZerolanProtocolWsServer
from event.event_data import PlaygroundConnectedEvent, PlaygroundDisconnectedEvent
from event.eventemitter import emitter
from services.playground.config import PlaygroundBridgeConfig
from services.playground.data import FileInfo, ScaleOperationResponse, CreateGameObjectResponse, \
    GameObject, ShowUserTextInputResponse, ServerHello, AddChatHistory, ShowTopMenu, SelectionItem, Arg_MenuItem
from services.playground.data import PlaySpeechResponse, LoadLive2DModelResponse
from services.res_server import get_temp_resource_endpoint, register_file


class Action(str, Enum):
    SHOW_MENU = "show_menu"
    PLAY_SPEECH = "play_speech"
    LOAD_LIVE2D_MODEL = "load_live2d_model"

    CLIENT_HELLO = "client_hello"
    SERVER_HELLO = "server_hello"

    LOAD_3D_MODEL = "load_model"
    UPDATE_GAMEOBJECTS_INFO = "update_gameobjects_info"
    QUERY_GAMEOBJECTS_INFO = "query_gameobjects_info"
    MODIFY_GAMEOBJECT_SCALE = "modify_gameobject_scale"
    CREATE_GAMEOBJECT = "create_gameobject"

    SHOW_USER_TEXT_INPUT = "show_user_text_input"
    ADD_HISTORY = "add_history"


_config = get_config()


class PlaygroundBridge(ZerolanProtocolWsServer):

    def __init__(self, config: PlaygroundBridgeConfig):
        super().__init__(host=config.host, port=config.port)
        self.gameobjects_info = {}
        self.server_ipv6, self.server_ipv4 = get_local_ip(True), get_local_ip()

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
        local_ip = get_local_ip(True)
        server_hello = ServerHello(ws_domain_or_ip=local_ip,
                                   ws_port=_config.service.playground.port,
                                   res_domain_or_ip=local_ip,
                                   res_port=_config.service.res_server.port)
        logger.debug(server_hello.model_dump_json())
        self.send(action=Action.SERVER_HELLO,
                  data=server_hello)
        emitter.emit(PlaygroundConnectedEvent())
        logger.info(f"`PlaygroundConnectedEvent` event emitted.")

    def _on_update_gameobjects_info(self, data: list[dict]):
        assert isinstance(data, list)
        self.gameobjects_info.clear()
        for info in data:
            go_info = GameObject.model_validate(info)
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
        audio_download_endpoint = get_temp_resource_endpoint(audio_path)
        self.send(action=Action.PLAY_SPEECH,
                  data=PlaySpeechResponse(bot_id=bot_id, audio_download_endpoint=audio_download_endpoint,
                                          bot_display_name=bot_name,
                                          transcript=transcript,
                                          audio_type=audio_type,
                                          sample_rate=sample_rate,
                                          channels=num_channels,
                                          duration=duration))

    def load_live2d_model(self, bot_id: str,
                          bot_display_name: str,
                          model_dir: str):
        """
        Load a specific Cubism Live2D model in the playground.
        :param bot_id:
        :param model_dir:
        :param bot_display_name:
        """
        assert os.path.exists(model_dir) and os.path.isdir(model_dir), f"{model_dir} is not a directory"
        zip_path = create_temp_file("live2d", ".zip", "model")
        compress_directory(model_dir, zip_path)
        model_download_endpoint = get_temp_resource_endpoint(zip_path)
        self.send(action=Action.LOAD_LIVE2D_MODEL, data=LoadLive2DModelResponse(
            bot_id=bot_id,
            bot_display_name=bot_display_name,
            model_dir=model_dir,
            model_download_endpoint=model_download_endpoint
        ))

    def load_3d_model(self, file_info: FileInfo):
        """
        Load a specific 3D model as a GameObject in the playground.
        :param file_info: FileInfo
        """
        self.send(action=Action.LOAD_3D_MODEL,
                  data=file_info, message="Load 3D model")

    def modify_game_object_scale(self, dto: ScaleOperationResponse):
        """
        Modify the scale of a specific GameObject in the playground.
        :param dto: ScaleOperationDTO
        """
        self.send(action=Action.MODIFY_GAMEOBJECT_SCALE, data=dto)

    def create_gameobject(self, dto: CreateGameObjectResponse):
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

    def get_gameobjects_info(self) -> list[GameObject]:
        """
        Get a list of the gameobjects info from the local cache.
        :return:
        """
        return to_value_list(self.gameobjects_info)

    def show_user_input_text(self, text: str):
        self.send(action=Action.SHOW_USER_TEXT_INPUT, data=ShowUserTextInputResponse(text=text))

    def add_history(self, username: str, role: str, text: str):
        self.send(action=Action.ADD_HISTORY, data=AddChatHistory(role=role, text=text, username=username))

    @typechecked
    def show_menu(self, menu_list: List[Arg_MenuItem], destroy_last: bool = True):
        items = []
        for idx, item in enumerate(menu_list):
            img_id = None
            if item.img_path is not None:
                img_id = register_file(item.img_path)
            interactive = item.interactive
            text = item.text if item.text is not None else "No text"
            items.append(SelectionItem(id=idx, interactive=interactive, text=text, img_id=img_id))
        menu = ShowTopMenu(
            uuid=str(uuid.uuid4()),
            items=items,
            destroy_last=destroy_last
        )
        self.send(action=Action.SHOW_MENU, data=menu)
