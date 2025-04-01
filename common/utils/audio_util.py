import io
from pathlib import Path

import numpy as np
import soundfile as sf
from pydub import AudioSegment
from scipy.io import wavfile as wavfile
from typeguard import typechecked

from common.io.file_type import AudioFileType


@typechecked
def get_audio_info(path: Path | str) -> (int, int, float):
    """
    Get audio info from path. Supported OGG, WAV, MP3, FLV and RAW. Also see AudioFileType.
    :param path: Audio file path.
    :return: sample_rate, num_channels, duration
    """
    suffix = Path(path).suffix
    if suffix[0] == '.':
        suffix = suffix[1:]

    if suffix == AudioFileType.OGG:
        audio = AudioSegment.from_ogg(path)
    elif suffix == AudioFileType.WAV:
        audio = AudioSegment.from_wav(path)
    elif suffix == AudioFileType.MP3:
        audio = AudioSegment.from_mp3(path)
    elif suffix == AudioFileType.FLV:
        audio = AudioSegment.from_flv(path)
    elif suffix == AudioFileType.RAW:
        audio = AudioSegment.from_raw(path)
    else:
        raise NotImplementedError()

    sample_rate = audio.frame_rate
    num_channels = audio.channels
    duration_ms = len(audio)
    duration = duration_ms / 1000.0

    return sample_rate, num_channels, duration


@typechecked
def get_audio_real_format(audio: bytes | str | Path) -> str:
    """
    Get real format of the audio.
    :param audio: Bytes data of the audio or the path of the audio file.
    :return: Real format of the audio.
    """
    if isinstance(audio, bytes):
        audio_bytes = audio
    elif isinstance(audio, str) or isinstance(audio, Path):
        with open(audio, "rb") as f:
            audio_bytes = f.read()
    else:
        raise TypeError("audio must be bytes or str type.")

    if audio_bytes.startswith(b'RIFF') and audio_bytes.find(b'WAVE') != -1:
        return AudioFileType.WAV
    elif audio_bytes.startswith(b'OggS'):
        return AudioFileType.OGG
    elif audio_bytes.startswith(b'FLV'):
        return AudioFileType.FLV
    elif audio_bytes.startswith(b'\xFF\xFB') or audio_bytes.startswith(b'\xFF\xF3'):
        return AudioFileType.MP3
    elif len(audio_bytes) > 0:
        return AudioFileType.RAW
    else:
        raise NotImplementedError("Unknown audio format.")


@typechecked
def from_ndarray_to_bytes(speech_chunk, sample_rate):
    """
    Convert numpy.ndarray data to bytes.
    :param speech_chunk: numpy.array.
    :param sample_rate: Sample rate of the speech chunk.
    :return:
    """
    wave_file = io.BytesIO()
    wavfile.write(filename=wave_file, rate=sample_rate, data=speech_chunk)
    return wave_file.getvalue()


@typechecked
def from_bytes_to_np_ndarray(bytes_data: bytes, dtype: str = "float32") -> (np.ndarray, int):
    """
    Convert byte data to numpy.ndarray format.
    :param bytes_data: Audio bytes of data.
    :param dtype: Default is float32.
    :return: The converted np.ndarray format data, sample rate.
    """
    wave_bytes_buf = io.BytesIO(bytes_data)
    data, samplerate = sf.read(wave_bytes_buf, dtype=dtype)
    return data, samplerate
