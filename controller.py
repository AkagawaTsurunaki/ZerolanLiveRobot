import asyncio
import json
import os

from loguru import logger

from chatglm3 import service as chatglm3_serv
from audio_player import service as audio_player_serv
from bilibili import service as bili_serv
from blip_img_cap.service import infer
from chatglm3.service import ModelRequest
from gptsovits import service as tts_serv
from obs.service import write_output
from scrnshot import service as scrn_serv
from tone_ana import service as tone_serv
from utils.util import is_blank

# 控制死循环
FLAG = True
LANG = 'zh'

# 一些默认路径
# OBS 字幕文件
DEFAULT_EMOTION_OUTPUT_PATH = '.tmp/emotion_output/emotion.txt'  # 默认心情标签输出文件夹
DEFAULT_LLM_OUTPUT_PATH = '.tmp/llm_output/chatglm3.txt'  # 默认大语言模型的输出路径
DEFAULT_DANMAKU_OUTPUT_PATH = '.tmp/danmaku/bilibili.txt'  # 默认弹幕的输出路径
# 模板文件
DEFAULT_CUSTOM_PROMPT_FILE_PATH = 'template/custom_prompt2.json'  # 用户自定义的提示词模板


def load_llm_sys_prompt():
    """
    加载用户自定义的提示词模板。
    如果在默认路径 {DEFAULT_CUSTOM_PROMPT_FILE_PATH} 下找不到对应的文件，那么就会创建一个。
    :return: ModelRequest
    """

    # 如果用户没有设置自己的自定义提示词，那么自动使用默认提示词
    if not os.path.exists(DEFAULT_CUSTOM_PROMPT_FILE_PATH):
        with open(file=DEFAULT_CUSTOM_PROMPT_FILE_PATH, mode='w+', encoding='utf-8') as file:
            model_req = ModelRequest(sys_prompt='', query='', temperature=1., top_p=1., history=[])
            json.dump(obj=model_req, fp=file, ensure_ascii=False, indent=4)
            logger.warning(
                f'已生成用户自定义的提示词模板，您可以到以下路径进行具体内容修改：{DEFAULT_CUSTOM_PROMPT_FILE_PATH}')

    with open(file=DEFAULT_CUSTOM_PROMPT_FILE_PATH, mode='r', encoding='utf-8') as file:
        json_value = json.load(file)
        model_req = ModelRequest(**json_value)
    logger.info(f'LLM 提示词模板加载完毕')
    return model_req


default_model_req: ModelRequest = load_llm_sys_prompt()


async def circle():
    """
    启动 ZerolanLiveRobot 生命周期
    每一个生命周期中，会先检查是否有可读的弹幕 Danmaku，并将弹幕内容拼接进 LLM 的 ModelRequest 请求中，
    待 LLM 服务按照流式返回一句整句 Sentence 后，再利用 LLM 服务分析其心情 Emotion，
    按照 Emotion 更改提示词，
    :return:
    """
    # 查看是否有可以选择的弹幕
    danmaku = bili_serv.select_01(k=3)

    if danmaku:
        logger.info(f'✅ [{danmaku.username}]({danmaku.uid}) {danmaku.msg}')

    img = scrn_serv.screen_cap()
    gamescn = infer(img, '') if img else None

    # 封装为一个模型请求体

    default_model_req.sys_prompt = ''
    if gamescn and danmaku:
        default_model_req.query = '{\n\t' + f'"{danmaku.username}": "{danmaku.msg}"' + '\n\t' + f'"gamescn": "{gamescn}"' + '\n' + '}'
    elif danmaku:
        default_model_req.query = '{\n\t' + f'"{danmaku.username}": "{danmaku.msg}"' + '\n' + '}'
    elif gamescn:
        default_model_req.query = '{\n\t' + f'"gamescn": "{gamescn}"' + '\n' + '}'
    else:
        return

    logger.info(f'🎮️ {gamescn}')
    # 其中 resp
    # 第1轮循环 resp = '我'
    # 第2轮循环 resp = '我是'
    # 第3轮循环 resp = '我是一个'
    # 第4轮循环 resp = '我是一个机器'
    # 第5轮循环 resp = '我是一个机器人'
    # 第6轮循环 resp = '我是一个机器人。'
    # ... 以此类推

    now = ''

    for model_resp in chatglm3_serv.stream_predict(query=default_model_req.sys_prompt + default_model_req.query,
                                                   history=default_model_req.history, top_p=default_model_req.top_p,
                                                   temperature=default_model_req.temperature):
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
        emotion = tone_serv.analyze_tone(sentence)
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
    bili_live_start = asyncio.create_task(bili_serv.start())
    while FLAG:
        await circle()
        await asyncio.sleep(1)
    await bili_live_start


if __name__ == '__main__':
    # 在调用 circle() 的地方，需要使用 asyncio.run() 或者在 asyncio 事件循环中运行该函数
    asyncio.run(start_life_cycle())
