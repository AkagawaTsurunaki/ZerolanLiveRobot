import numpy as np
from loguru import logger

from common.buffer.asr_res_buf import AudioBuffer, ASRResultBuffer, ASRResultBufferObject
from common.utils.audio_util import from_ndarray_to_bytes
from services.device.microphone import Microphone
from pipeline.asr import ASRPipeline
from services.vad.strategy import EasyEnergyVad
from zerolan_live_robot_data.data.asr import ASRModelStreamQuery

sample_rate = 16000
channels = 1

pipeline = ASRPipeline()

mp = Microphone()
mp.open()

speech_buf = AudioBuffer()
vad = EasyEnergyVad()
asr_buf = ASRResultBuffer()

cache: ASRResultBufferObject | None = None

for chunk in mp.stream():

    speech_chunk = np.frombuffer(chunk, dtype=np.float32)
    speech = vad.check_stream(speech_chunk)
    speech_buf.append(speech_chunk)
    if speech is not None:
        wave_bytes_data = from_ndarray_to_bytes(speech_buf.read_all(), sample_rate)
        q = ASRModelStreamQuery(is_final=False, audio_data=wave_bytes_data, sample_rate=sample_rate, channels=channels,
                                media_type="ndarray/np.float32")
        p = pipeline.stream_predict(q)
        if p:
            logger.warning(p.transcript)
            cache = ASRResultBufferObject(p.transcript)
    else:
        if cache:
            asr_buf.append(cache)
            speech_buf.flush()
            cache = None
            res: ASRResultBufferObject = asr_buf.get(-1)
            logger.info(f"确定结果: {res.asr_result}")
