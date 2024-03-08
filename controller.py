import asyncio
import json

from loguru import logger

import chatglm3
import emo
from emo import Emotion
import gptsovits
from audio_player import service as audio_player_serv
from bilibili import service as bili_serv
from chatglm3.api import ModelRequest, stream_chat
from gptsovits import service as tts_serv

# 控制死循环
FLAG = True
LANG = 'zh'


def load_sys_prompt():
    with open(file='template/game_prompt.json', mode='r', encoding='utf-8') as file:
        json_value = json.load(file)
        model_req = ModelRequest(**json_value)
    return model_req


default_model_req = load_sys_prompt()


def write_output(danmaku, text: str, emotion: Emotion):
    with open(file='.tmp/emotion_output/emotion.txt', mode='w', encoding='utf-8') as file:
        file.write(emotion.id)
    with open(file='.tmp/llm_output/chatglm3.txt', mode='w', encoding='utf-8') as file:
        file.write(f'> {danmaku.username}: {danmaku.msg} \n[{emotion.id}] {text}')


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

    # 查看是否有可以选择的弹幕
    danmaku = bili_serv.select_01(k=3)

    if not danmaku:
        return
    logger.info(f'✅ 选择了 1 条弹幕：[{danmaku.username}]({danmaku.uid}) {danmaku.msg}')

    # 封装为一个模型请求体

    default_model_req.sys_prompt = ''
    default_model_req.query = f'[{danmaku.username}] {danmaku.msg}'

    # 其中 resp
    # 第1轮循环 resp = '我'
    # 第2轮循环 resp = '我是'
    # 第3轮循环 resp = '我是一个'
    # 第4轮循环 resp = '我是一个机器'
    # 第5轮循环 resp = '我是一个机器人'
    # 第6轮循环 resp = '我是一个机器人。'
    # ... 以此类推

    now = ''

    for model_resp in stream_chat(default_model_req):
        resp = model_resp.response
        # 按照标点符号切割句子
        if not resp:
            continue

        if resp[-1] not in ['。', '！', '？', '!', '?']:
            continue

        # 保留单句
        sentence = resp[len(now): len(resp)]
        now = now + sentence

        if is_blank(sentence):
            continue

        if len(sentence) < 6:
            continue

        # 更新历史

        default_model_req.history = model_resp.history
        logger.debug(f'当前 LLM 历史记录：{len(default_model_req.history)}')

        # 分析句子的情感倾向
        emotion = emo.ana_emo(chatglm3.__name__, sentence)
        logger.info(f'心情：{emotion.id}')

        # 根据心情切换 Prompt
        tts_serv.change_prompt(emotion.refer_wav_path, emotion.prompt_text, emotion.prompt_language)

        # TTS 任务
        wav_file_path = tts_serv.predict(sentence, LANG)

        # 写入心情
        write_output(danmaku, sentence, emotion)

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
    # 初始化心理模块
    emo.load_emo_list(gptsovits.__name__)
    bili_live_start = asyncio.create_task(bili_serv.start())
    while FLAG:
        await circle()
        await asyncio.sleep(1)
    await bili_live_start


if __name__ == '__main__':
    # 在调用 circle() 的地方，需要使用 asyncio.run() 或者在 asyncio 事件循环中运行该函数
    asyncio.run(start_life_cycle())
