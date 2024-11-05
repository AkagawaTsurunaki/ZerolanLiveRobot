from zerolan.data.data.asr import ASRModelQuery
from pipeline.asr import ASRPipeline

pipeline = ASRPipeline()

p = pipeline.predict(ASRModelQuery(
    audio_path=R"tests/resources/test-asr-zh-48000.wav",
    media_type='wav',
    sample_rate=16000,
    channels=1))

print(p.transcript)