import numpy as np
from loguru import logger

from common.buffer.asr_res_buf import AudioBuffer, ASRResultBuffer, ASRResultBufferObject
from common.config.service_config import ASRServiceConfig as config
from common.utils.audio_util import from_ndarray_to_bytes
from gui.toast import toast
from manager.device.microphone import Microphone
from services.asr.pipeline import ASRPipeline, ASRModelStreamQuery
from services.vad.strategy import EasyEnergyVad

sample_rate = config.sample_rate
channels = config.channels

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
            toast.info(res.asr_result)
