from typing import Any

from flask import Request
from loguru import logger

from common.utils import file_util


def save_request_image(request: Request, prefix: str) -> str:
    # 如果是 multipart/form-data 格式，那么尝试获取图像文件
    image_file = request.files.get('image', None)
    if image_file is None:
        raise ValueError('请求中 image 字段无图片数据')

    file_type = image_file.mimetype.split("/")[-1]
    if len(file_type) != 0:
        assert file_type in ["jpg", "png"], "不支持的图像类型"
    else:
        file_type = "png"

    temp_file_path = file_util.create_temp_file(prefix=prefix, suffix=f".{file_type}", tmpdir="image")
    image_file.save(temp_file_path)
    logger.debug(f"临时文件创建于：{temp_file_path}")

    return temp_file_path


def get_request_audio_file(request: Request):
    # 如果是 multipart/form-data 格式，那么尝试获取音频文件
    audio_file = request.files.get('audio', None)
    if audio_file is None:
        raise ValueError('请求中 audio 字段无音频数据')
    return audio_file


def save_request_audio(request: Request, prefix: str) -> str:
    # 如果是 multipart/form-data 格式，那么尝试获取音频文件
    audio_file = get_request_audio_file(request)

    file_type = audio_file.mimetype.split("/")[-1]
    if len(file_type) != 0:
        if file_type == "wave":
            file_type = "wav"
        assert file_type in ["wav", "mp3", "ogg"], "不支持的音频类型"
    else:
        file_type = "wav"

    temp_file_path = file_util.create_temp_file(prefix=prefix, suffix=f".{file_type}", tmpdir="audio")
    audio_file.save(temp_file_path)
    logger.debug(f"临时文件创建于：{temp_file_path}")

    return temp_file_path


def get_obj_from_json(request: Request, type: Any) -> Any:
    # 如果是 multipart/form-data 格式，那么尝试获取 JSON 反序列化后的对象
    json_str = request.form.get("json", None)
    if json_str is None:
        raise ValueError('请求中 json 字段无 JSON 数据')
    assert hasattr(type, "from_json"), f"无法将 JSON 数据转换至 {type}"
    obj = type.from_json(json_str)
    return obj


def urljoin(host: str, port: int, path: str = None, protocol: str = 'http'):
    """
    根据协议、主机、端口号和路径，拼接 URL。
    Args:
        host: 主机，例如 127.0.0.1。
        port: 端口号，例如 11451。
        path: 路径，例如 /test/speak。
        protocol: 协议，例如 http、https等。

    Returns:

    """
    assert host and port and protocol
    assert isinstance(host, str) and isinstance(port, int) and isinstance(protocol, str)

    url = f"{protocol}://{host}:{port}"
    if path:
        assert isinstance(path, str)
        assert path[0] == '/', f'"path" should begin with "/".'
        url += path

    return url
