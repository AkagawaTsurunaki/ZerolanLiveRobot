import io

from common.utils.file_util import create_temp_file


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
    wav_path = create_temp_file(prefix="tts", suffix=f".{format}", tmpdir="audio")
    with open(wav_path, "wb") as f:
        f.write(wave_data)
    return wav_path
