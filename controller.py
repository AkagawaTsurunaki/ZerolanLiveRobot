from audio_player import service as audio_player_serv
from bilibili import service as bili_serv
from chatglm3 import service as llm_serv
from gptsovits import service as tts_serv

import asyncio


async def circle():
    # 先确认当前是否有音频正在播放
    if not audio_player_serv.is_over():
        return

    # 查看是否有可以选择的弹幕
    danmaku = bili_serv.select_01(k=5)
    if not danmaku:
        return

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

    async for resp, _, _ in llm_serv.stream_predict(danmaku.msg):

        # 按照标点符号切割句子
        if resp[-1] not in ['。', '！', '？']:
            continue

        # 保留单句
        sentence = resp[len(now): len(resp)]
        now = now + sentence

        # TTS 任务
        task_tts = asyncio.create_task(tts_serv.predict(sentence, 'zh'))

        # 音频播放任务
        task_audio_play = asyncio.create_task(audio_player_serv.play(await task_tts))

        # 继续LLM的运算
        await asyncio.sleep(0)  # 让出控制权，让事件循环执行其他任务

        # 等待音频播放完成
        await task_audio_play

# 在调用 circle() 的地方，需要使用 asyncio.run() 或者在 asyncio 事件循环中运行该函数
