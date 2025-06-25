import json
import os
from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

from flask import Flask, abort, send_file, request
from loguru import logger
from openai import BaseModel
from typeguard import typechecked

from common.concurrent.abs_runnable import ThreadRunnable
from common.io.file_sys import fs
from common.io.file_type import AudioFileType
from common.utils.audio_util import get_audio_real_format
from event.event_data import DeviceScreenCapturedEvent, DeviceMicrophoneVADEvent
from event.event_emitter import emitter
from manager.config_manager import get_config

RESOURCE_TYPES = {
    "audio": "audio",
    "image": "image",
    "video": "video",
    "model": "model",
}

_config = get_config()


class HTTPResponseBody(BaseModel):
    code: int = 0  # 0 means successful operation
    message: str
    data: Any = None


class _AudioMetadata(BaseModel):
    channels: int
    sample_rate: int


# Path => file_id
_files: Dict[str, str] = {}


@typechecked
def register_file(path: str | Path) -> str:
    global _files
    path = Path(path).absolute()
    assert path.exists(), f"No such file: {path}"

    file_id = _files.get(str(path), None)
    if file_id is None:
        file_id = str(uuid4())
        _files[str(path)] = file_id

    return file_id


class ResourceServer(ThreadRunnable):
    def name(self):
        return "ResourceServer"

    def stop(self):
        super().stop()

    def __init__(self, host: str, port: int):
        super().__init__()
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self.init()

    def init(self):
        @self.app.route('/resource/temp/<resource_type>/<filename>')
        def serve_resource(resource_type: str, filename):
            """
            根据请求的资源类型和文件名，从指定文件夹中提供文件。
            """
            # 检查资源类型是否有效
            if resource_type not in RESOURCE_TYPES:
                abort(404, description="Invalid resource type")

            # 构造文件路径
            file_path = str(os.path.join(resource_type, filename))
            file_path = os.path.join(fs.temp_dir, file_path)

            # 检查文件是否存在
            if not os.path.exists(file_path):
                abort(404, description="File not found")

            return send_file(file_path)

        @self.app.route('/resource/file')
        def handle_resource_file():
            global _files
            file_id = request.args.get('file_id')
            assert file_id is not None

            for path, id in _files.items():
                if id == file_id:
                    logger.info(f"File (id={file_id}) is found: {path}")
                    return send_file(path)

            logger.warning(f"No file (id={file_id}). Current files map is: \n{json.dumps(_files, indent=4)}")

            abort(404, description="File not found")

        @self.app.route("/playground/camera", methods=["POST"])
        def camera_send():
            try:
                logger.info("Get camera image from client.")
                file = request.files.get("image", None)
                image_type = None
                if file.content_type == "image/png":
                    image_type = 'png'
                elif file.content_type == "image/jpeg":
                    image_type = 'jpeg'
                elif file.content_type == "image/jpg":
                    image_type = 'jpg'

                img_path = fs.create_temp_file_descriptor(prefix="imgcap", suffix=f".{image_type}", type="image")
                file.save(img_path)
                file.close()

                emitter.emit(DeviceScreenCapturedEvent(img_path=str(img_path), is_camera=True))
                return HTTPResponseBody(message="OK").model_dump()
            except Exception as e:
                logger.exception(e)
                return HTTPResponseBody(message="Failed to receive your image data.", code=1).model_dump()

        @self.app.route("/playground/microphone", methods=["POST"])
        def microphone_send():
            # channels: int
            # sample_rate: int
            # audio: bytes
            try:
                logger.info("Get microphone audio from client.")

                # Decode from JSON binary data to get metadata about audio file
                audio_metadata = request.files.get("metadata", None)
                assert audio_metadata is not None, "Invalid audio metadata"
                audio_metadata = audio_metadata.stream.read()
                audio_metadata = audio_metadata.decode("utf-8")
                audio_metadata = _AudioMetadata.model_validate_json(audio_metadata)

                # Read data from audio file
                file = request.files.get("audio", None)
                audio_data = file.stream.read()

                # Check audio data type
                if file.content_type == "audio/mp3":
                    audio_type = AudioFileType.MP3
                elif file.content_type == "audio/wav":
                    audio_type = AudioFileType.WAV
                elif file.content_type == "audio/ogg":
                    audio_type = AudioFileType.OGG
                else:
                    audio_type = get_audio_real_format(audio_data)

                if audio_metadata.channels > 2:
                    logger.warning(f"Is that right? \n{audio_metadata}")
                emitter.emit(DeviceMicrophoneVADEvent(speech=audio_data,
                                                      channels=audio_metadata.channels,
                                                      sample_rate=audio_metadata.sample_rate,
                                                      audio_type=audio_type))

                return HTTPResponseBody(message="OK").model_dump()
            except Exception as e:
                logger.exception(e)
                return HTTPResponseBody(message="Failed to receive your audio data.", code=1).model_dump()

    def start(self):
        super().start()
        self.app.run(host=self.host, port=self.port, debug=True, use_reloader=False)
