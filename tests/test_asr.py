from services.asr.pipeline import ASRModelQuery
from pipeline.asr import ASRPipeline

pipeline = ASRPipeline()

p = pipeline.predict(ASRModelQuery(
    audio_path=R"",
    media_type='wav',
    sample_rate=16000,
    channels=1))

print(p.transcript)