import time
from common.decorator import log_run_time
from zerolan.data.pipeline.llm import LLMQuery, Conversation, RoleEnum, LLMPrediction
from zerolan.data.pipeline.tts import TTSQuery
from common.config import get_config
from zerolan.ump.pipeline.llm import LLMPipeline

from common.enumerator import Language

_config = get_config()

llm_pipeline = LLMPipeline(_config.pipeline.llm)


@log_run_time()
def llm_predict_with_history():
    query = LLMQuery(text="你现在能和我玩游戏吗？",
                     history=[Conversation(role=RoleEnum.user, content="你现在是一只猫娘，请在句尾始终带上喵"),
                              Conversation(role=RoleEnum.assistant, content="好的，主人喵")])
    prediction = llm_pipeline.predict(query)
    return prediction

@log_run_time()
def tts(prediction: LLMPrediction):
    text = prediction.response if prediction is not None else "这是一段随机生成的文字内容！我要喵喵叫！你听见了嘛？主人？"
    query = TTSQuery(text=text,
                     text_language=Language.ZH,
                     refer_wav_path="/home/akagawatsurunaki/workspace/ZerolanLiveRobot/resources/static/prompts/tts/[zh][Default]喜欢游戏的人和擅长游戏的人有很多不一样的地方，老师属于哪一种呢？.wav",
                     prompt_text="喜欢游戏的人和擅长游戏的人有很多不一样的地方，老师属于哪一种呢？",
                     prompt_language=Language.ZH)

    first_rcv = False
    for prediction in tts.stream_predict(query):
        if not first_rcv:
            first_rcv = True
            t_first_chunk = time.time()
            print(f"Post data got: {time.time()}")
            print(f"Elapsed time: {t_first_chunk - t_start_post}")