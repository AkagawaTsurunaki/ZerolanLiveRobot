import numpy as np
from loguru import logger

from common.buffer.asr_res_buf import ASRResultBuffer
from manager.device.microphone import Microphone
from services.asr.paraformer.model import SpeechParaformerModel
from services.vad.strategy import EasyEnergyVad

m = SpeechParaformerModel()
m.load_model()

mp = Microphone()
mp.open()

vad = EasyEnergyVad()
buf = ASRResultBuffer()

cache = None

for chunk in mp.stream():
    speech_chunk = np.frombuffer(chunk, dtype=np.float32)
    speech = vad.check_stream(speech_chunk)
    if speech is not None:
        p = m.stream_predict(speech)
        if p:
            logger.warning(p.transcript)
            cache = p
    else:
        if cache:
            buf.write(cache)
            cache = None
