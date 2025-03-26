import os.path

from loguru import logger
from websockets.sync.connection import Connection

from common.utils.audio_util import check_audio_format, check_audio_info
from common.utils.file_util import create_temp_file, compress_directory
from common.ws.proto.protocol_pb2 import ClientHello  # type: ignore
from common.ws.safe_zrl_ws import BaseAction, SafeZerolanProtocolWebSocketServer
from event.event_data import PlaygroundConnectedEvent, PlaygroundDisconnectedEvent
from event.eventemitter import emitter
from services.playground.proto import bridge_pb2


class Action(BaseAction):
    PLAY_SPEECH = "play_speech"
    LOAD_LIVE2D_MODEL = "load_live2d_model"

    LOAD_3D_MODEL = "load_model"
    UPDATE_GAMEOBJECTS_INFO = "update_gameobjects_info"
    QUERY_GAMEOBJECTS_INFO = "query_gameobjects_info"
    MODIFY_GAMEOBJECT_SCALE = "modify_gameobject_scale"
    CREATE_GAMEOBJECT = "create_gameobject"

    SHOW_USER_TEXT_INPUT = "show_user_text_input"
    ADD_HISTORY = "add_history"


class PlaygroundBridge(SafeZerolanProtocolWebSocketServer):
    def name(self):
        return "ZerolanPlaygroundBridge"

    def __init__(self, host: str, port: int, password: str):
        super().__init__(host, port, password)

        @self.on_close()
        def on_disconnect(conn: Connection, code: int, reason: str):
            emitter.emit(PlaygroundDisconnectedEvent(ws_id=str(conn.id), code=code, reason=reason))

        @self.on_verified()
        def on_verified(_: Connection, client_hello: ClientHello):
            logger.info(f"ZerolanPlayground client is connected and verified.")
            emitter.emit(PlaygroundConnectedEvent(namespace=client_hello.namespace))
            logger.info(f"`PlaygroundConnectedEvent` event emitted.")

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
        with open(audio_path, 'rb') as f:
            data = bridge_pb2.PlaySpeech(
                bot_id=bot_id,
                bot_display_name=bot_name,
                audio_type=audio_type,
                sample_rate=sample_rate,
                channels=num_channels,
                duration=duration,
                transcript=transcript,
                audio_data=f.read()
            )
            self.send(action=Action.PLAY_SPEECH, data=data, message="Play speech")

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
        with open(zip_path, 'rb') as f:
            data = bridge_pb2.LoadLive2DModel(
                bot_id=bot_id,
                bot_display_name=bot_display_name,
                model_zip=f.read()
            )
            self.send(action=Action.LOAD_LIVE2D_MODEL, data=data)

    def show_user_input_text(self, text: str):
        self.send(action=Action.SHOW_USER_TEXT_INPUT, data=bridge_pb2.ShowUserTextInput(text=text))

    def add_history(self, username: str, role: str, text: str):
        self.send(action=Action.ADD_HISTORY, data=bridge_pb2.AddHistory(role=role, text=text, username=username))

    def load_3d_model(self, file_id: str, file_type: str, path: str):
        """
        Load a specific 3D model as a GameObject in the playground.
        :param path:
        :param file_type:
        :param file_id:
        """
        with open(path, 'rb') as f:
            data = bridge_pb2.Model3DFile(
                file_id=file_id,
                file_type=file_type,
                file_data=f.read()
            )
            self.send(action=Action.LOAD_3D_MODEL,
                      data=data, message="Load 3D model")
