import io


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
