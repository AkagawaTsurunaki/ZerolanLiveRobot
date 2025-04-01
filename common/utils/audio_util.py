import io
from pathlib import Path
import numpy as np
from pydub import AudioSegment

from common.io.file_sys import fs

def from_bytes_to_np_ndarray(bytes_data: bytes, dtype: str = "float32") -> (np.ndarray, int):
    """
    Convert byte data to np.ndarray format.
    Args:
        bytes_data: Audio bytes of data.
        dtype: Default is float32.

    Returns: Returns the converted np.ndarray format data, sample rate.

    """
    import soundfile as sf

    wave_bytes_buf = io.BytesIO(bytes_data)
    data, samplerate = sf.read(wave_bytes_buf, dtype=dtype)
    return data, samplerate


def from_ndarray_to_bytes(speech_chunk, sample_rate):
    from scipy.io import wavfile as wavfile

    wave_file = io.BytesIO()
    wavfile.write(filename=wave_file, rate=sample_rate, data=speech_chunk)
    return wave_file.getvalue()


def check_audio_info(file_path) -> (int, int, float):
    suffix = Path(file_path).suffix
    if suffix == ".ogg":
        audio = AudioSegment.from_ogg(file_path)
    elif suffix == ".wav":
        audio = AudioSegment.from_wav(file_path)
    elif suffix == ".mp3":
        audio = AudioSegment.from_mp3(file_path)
    else:
        raise NotImplementedError()
    sample_rate = audio.frame_rate
    num_channels = audio.channels
    duration_ms = len(audio)
    duration = duration_ms / 1000.0
    return sample_rate, num_channels, duration


# def check_wav_info(file_path) -> (int, int, float):
#     import wave
#     # 打开WAV文件
#     wav_file = wave.open(file_path, mode='rb')
#     # 获取采样率
#     sample_rate = wav_file.getframerate()
#     # 获取通道数
#     num_channels = wav_file.getnchannels()
#     # 获取时长
#     duration = wav_file.getnframes() / sample_rate
#     # 关闭文件
#     wav_file.close()
#     return sample_rate, num_channels, duration


def check_audio_format(audio) -> str:
    if isinstance(audio, bytes):
        audio_bytes = audio
    elif isinstance(audio, str):
        with open(audio, "rb") as f:
            audio_bytes = f.read()
    if audio_bytes.startswith(b'RIFF') and audio_bytes.find(b'WAVE') != -1:
        return 'wav'
    elif audio_bytes.startswith(b'OggS'):
        return 'ogg'
    else:
        raise NotImplementedError()


def save_tmp_audio(wave_data: bytes):
    format = check_audio_format(wave_data)
    wav_path = fs.create_temp_file_descriptor(prefix="tts", suffix=f".{format}", type="audio")
    with open(wav_path, "wb") as f:
        f.write(wave_data)
    return wav_path
