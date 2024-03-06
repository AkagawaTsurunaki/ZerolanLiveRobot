import asyncio
import json
from dataclasses import asdict

import requests
from loguru import logger

# 配置 Loguru，设置日志文件和最低日志级别为 INFO
logger.add("file.log", level="INFO")

from audio_player import service as audio_player_serv
from bilibili import service as bili_serv
from chatglm3.api import ModelRequest, ModelResponse
from gptsovits import service as tts_serv

# 控制死循环
FLAG = True


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


def stream_llm_output(model_req: ModelRequest):
    response = requests.post('http://127.0.0.1:8721/predict', stream=True, json=asdict(model_req))

    for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
        if chunk:
            try:
                json_value = json.loads(chunk, strict=False)
            except Exception as e:
                continue

            yield ModelResponse(**json_value)


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
    你现在是一名猫娘，正在哔哩哔哩上直播，请与观众们友好互动。
    以下是弹幕的格式
    '''
    [用户名] 弹幕所说的话
    '''
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

    # async for resp, _, _ in llm_serv.stream_predict(danmaku.msg):
    for model_resp in stream_llm_output(model_req):
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
        task_tts = asyncio.create_task(tts_serv.predict(sentence, 'zh'))

        # 音频播放任务
        task_audio_play = asyncio.create_task(audio_player_serv.play(wav_file_path=await task_tts, transcript=resp))

        # 继续LLM的运算
        await asyncio.sleep(0)  # 让出控制权，让事件循环执行其他任务

        # 等待音频播放完成
        await task_audio_play


async def start_life_cycle():
    """
    启动生命周期
    :return:
    """
    # threading.Thread()
    bili_live_start = asyncio.create_task(bili_serv.start())
    while FLAG:
        await circle()
        await asyncio.sleep(1)
    await bili_live_start


if __name__ == '__main__':
    # 在调用 circle() 的地方，需要使用 asyncio.run() 或者在 asyncio 事件循环中运行该函数
    asyncio.run(start_life_cycle())
