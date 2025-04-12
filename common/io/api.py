from pathlib import Path

from typeguard import typechecked

from common.io.file_sys import fs
from common.io.file_type import AudioFileType, ImageFileType
from common.utils.audio_util import get_audio_real_format


@typechecked
def save_image(image_bytes: bytes, format: ImageFileType, prefix: str | None = None) -> str:
    """
    Save bytes data as an image to temp file.
    :param prefix: Filename prefix.
    :param image_bytes: Bytes data
    :param format: Format of the image data.
    :return: Saved image path.
    """
    img_path = fs.create_temp_file_descriptor(prefix=prefix, suffix=f".{format}", type="image")

    # Attention: DO NOT use built-in open function, this may cause PermissionDeniedError on Windows platform!
    with img_path.open("wb+") as image_file:
        image_file.write(image_bytes)
        return img_path


@typechecked
def save_audio(wave_data: bytes, format: AudioFileType | None = None, prefix: str | None = None) -> Path:
    """
    Save audio data to the temp file.
    :param wave_data: Bytes of audio data.
    :param format: Format of the audio data.
    :param prefix: Filename prefix.
    :return: Saved audio path.
    """
    if format is None:
        format = get_audio_real_format(wave_data)
    wav_path = fs.create_temp_file_descriptor(prefix=prefix, suffix=f".{format.value}", type="audio")

    # Attention: DO NOT use built-in open function, this may cause PermissionDeniedError on Windows platform!
    with wav_path.open("wb+") as f:
        f.write(wave_data)
    return Path(wav_path)
