import numpy as np
from zerolan.data.pipeline.asr import ASRQuery, ASRStreamQuery

from common.utils.audio_util import from_bytes_to_np_ndarray
from common.utils.file_util import read_yaml
from pipeline.synch.asr import ASRPipeline
from pipeline.config.config import ASRPipelineConfig

_config = read_yaml("./resources/config.test.yaml")

_asr = ASRPipeline(ASRPipelineConfig(
    model_id=_config['asr']['model_id'],
    predict_url=_config['asr']['predict_url'],
    stream_predict_url=_config['asr']['stream_predict_url'],
))


def test_asr_predict():
    query = ASRQuery(audio_path="resources/tts-test.wav", channels=2)
    prediction = _asr.predict(query)
    assert prediction, f"Test failed"
    print(prediction.transcript)
    assert "我是" in prediction.transcript, f"Test failed"


def test_asr_stream_predict():
    audio_path = "resources/tts-test.wav"
    with open(audio_path, "rb") as f:
        data, samplerate = from_bytes_to_np_ndarray(f.read())
        print(data.shape)
        data = data[:, 0]
        print(data.shape)
        num_chunk = 4
        chunk_size = data.shape[0] // num_chunk
        buffer = np.zeros(shape=(1, 1), dtype=np.float32)
        for i in range(num_chunk):
            chunk: np.ndarray = data[i * chunk_size: (i + 1) * chunk_size]
            is_final = i == num_chunk - 1
            buffer = np.append(buffer, chunk)
            query = ASRStreamQuery(is_final=is_final, audio_data=buffer.tobytes(), channels=1, media_type='raw',
                                   sample_rate=samplerate)
            for prediction in _asr.stream_predict(query):
                assert prediction, f"Test failed"
                print(prediction.transcript)
                assert "我" in prediction.transcript, f"Test failed"
