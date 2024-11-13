from dataclasses import dataclass

from dataclasses_json import dataclass_json
from zerolan.data.data.tts import TTSQuery, TTSPrediction

from pipeline.tts import TTSPipeline
from services.device.speaker import Speaker


@dataclass_json
@dataclass
class NewQuery(TTSQuery):
    cut_punc: str = "，。"


query = NewQuery(
    text="请注意，这个脚本只是一个基本的检查，它不会处理所有可能的边缘情况，比如文件可能被截断或者损坏。在实际应用中，可能需要更复杂的检查，包括对文件头后面的数据进行验证。在使用这个脚本之前，确保你已经有了要检查的bytes数据，并且将其赋值给audio_bytes变量。这个脚本将打印出音频格式是WAV、OGG还是未知格式。",
    text_language="zh",
    refer_wav_path=R"/static/audio/momoi/[zh][正常]喜欢游戏的人和擅长游戏的人有很多不一样的地方，老师属于哪一种呢？.wav",
    prompt_text="喜欢游戏的人和擅长游戏的人有很多不一样的地方，老师属于哪一种呢？",
    prompt_language="zh",
    cut_punc="，。")

pipeline = TTSPipeline()
speaker = Speaker()


def test_tts_predict():
    prediction = pipeline.predict(query)

    print(len(prediction.wave_data))


def test_tts_stream_predict():
    for prediction in pipeline.stream_predict(query):
        prediction: TTSPrediction
        print(prediction.wave_data)
        speaker.playsound(prediction.wave_data)


test_tts_stream_predict()
