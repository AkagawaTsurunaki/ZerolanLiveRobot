import io
import subprocess

import numpy as np


def convert_to_mono(input_file, output_file, sample_rate: int = 16000):
    # ffmpeg command to convert audio to mono wav
    command = [
        'ffmpeg',
        '-i', input_file,  # input file
        '-ac', '1',  # set number of audio channels to 1 (mono)
        '-ar', str(sample_rate),  # set audio sample rate
        '-c:a', 'pcm_s16le',  # set audio codec to PCM 16-bit little-endian
        output_file  # output file
    ]

    # Run ffmpeg command
    subprocess.run(command, check=True)


def from_file_to_np_array(input_file: str, dtype: str = "float32") -> (np.ndarray, int):
    import soundfile as sf

    data, samplerate = sf.read(input_file, dtype=dtype)
    return data, samplerate


def from_bytes_to_np_ndarray(bytes_data: bytes, dtype: str = "float32") -> (np.ndarray, int):
    """
    从字节数据转化为 np.ndarray 格式。
    Args:
        bytes_data: 音频字节数据。
        dtype: 默认为 float32。

    Returns: 返回转换后的 np.ndarray 格式数据，采样率。

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


def check_wav_info(file_path) -> (int, int, float):
    import wave
    # 打开WAV文件
    wav_file = wave.open(file_path, mode='rb')
    # 获取采样率
    sample_rate = wav_file.getframerate()
    # 获取通道数
    num_channels = wav_file.getnchannels()
    # 获取时长
    duration = wav_file.getnframes() / sample_rate
    # 关闭文件
    wav_file.close()
    return sample_rate, num_channels, duration
