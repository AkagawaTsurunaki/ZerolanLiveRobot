import asyncio

from loguru import logger

import chatglm3
import emo
import gptsovits
from audio_player import service as audio_player_serv
from bilibili import service as bili_serv
from chatglm3.api import ModelRequest, stream_chat
from gptsovits import service as tts_serv

# 控制死循环
FLAG = True
LANG = 'zh'


def is_blank(s: str):
    """
    判断字符串是否为空字符串
    :param s: 待判断的字符串
    :return: 如果字符串为空返回 True，否则返回 False
    """
    if s is None:
        return True
    if s == '':
        return True
    if "".isspace():
        return True
    return False


async def circle():
    # # 先确认当前是否有音频正在播放
    # if not audio_player_serv.is_over():
    #     return
    #
    # 查看是否有可以选择的弹幕
    danmaku = bili_serv.select_01(k=5)

    if not danmaku:
        return
    logger.info(f'✅ 选择了 1 条弹幕：[{danmaku.username}]({danmaku.uid}) {danmaku.msg}')

    # 封装为一个模型请求体

    sys_prompt = """
    你现在是一名叫幼刀丛雨的猫娘，正在哔哩哔哩上直播，请与观众们友好互动。
    以下是弹幕的格式
    '''
    [用户名] 弹幕所说的话
    '''
    请注意你的回复不能超过超过50字，对话的情感要丰富，有时生气，有时开心，有时傲娇，有时搞怪。
    """
    query = f'[{danmaku.username}] {danmaku.msg}'

    # TODO: 历史记忆
    model_req = ModelRequest(
        sys_prompt=sys_prompt,
        query=query,
        history=[],
        temperature=1.,
        top_p=1.
    )

    # 有弹幕可读
    # 其中 resp
    # 第1轮循环 resp = '我'
    # 第2轮循环 resp = '我是'
    # 第3轮循环 resp = '我是一个'
    # 第4轮循环 resp = '我是一个机器'
    # 第5轮循环 resp = '我是一个机器人'
    # 第6轮循环 resp = '我是一个机器人。'
    # ... 以此类推

    now = ''

    for model_resp in stream_chat(model_req):
        resp = model_resp.response
        # 按照标点符号切割句子
        if not resp:
            continue

        if resp[-1] not in ['。', '！', '？', '!', '?']:
            continue

        # 保留单句
        sentence = resp[len(now): len(resp)]
        now = now + sentence

        # TTS 任务
        if is_blank(sentence):
            continue

        # 分析句子的情感倾向
        emotion = emo.ana_emo(chatglm3.__name__, sentence)
        logger.info(f'心情：{emotion.id}')
        tts_serv.change_prompt(emotion.refer_wav_path, emotion.prompt_text, emotion.prompt_language)
        wav_file_path = tts_serv.predict(sentence, LANG)

        # 如果音频文件不为空（如果服务器出错，则为空），则播放音频
        if not wav_file_path:
            logger.warning(f'这条语音未能合成：[{LANG}] {sentence}')
            continue
        audio_player_serv.play(wav_file_path=wav_file_path, transcript=resp)

        # 继续LLM的运算
        await asyncio.sleep(0)  # 让出控制权，让事件循环执行其他任务


async def start_life_cycle():
    """
    启动生命周期
    :return:
    """
    # threading.Thread()
    emo.load_emo_list(gptsovits.__name__)
    bili_live_start = asyncio.create_task(bili_serv.start())
    while FLAG:
        await circle()
        await asyncio.sleep(1)
    await bili_live_start


if __name__ == '__main__':
    # 在调用 circle() 的地方，需要使用 asyncio.run() 或者在 asyncio 事件循环中运行该函数
    asyncio.run(start_life_cycle())
