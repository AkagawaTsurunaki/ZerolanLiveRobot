import json
import threading
from dataclasses import dataclass
from os import PathLike
from typing import List

from loguru import logger

import audio_player.service
import chatglm3.api
from bilibili import service as bili_serv
from bilibili.service import Danmaku
from blip_img_cap import service as blip_serv
from gptsovits import service as gptsovits_serv
from obs import service as obs_serv
from scrnshot import service as scrn_serv
from tone_ana import service as tone_serv
from utils.util import is_blank

HISTORY: List[dict] = []
CUSTOM_PROMPT_PATH: str = 'template/custom_prompt.json'
LANG = 'zh'


def load_custom_history():
    global HISTORY, CUSTOM_PROMPT_PATH
    with open(file=CUSTOM_PROMPT_PATH, mode='r', encoding='utf-8') as file:
        json_value: dict = json.load(file)
        HISTORY = json_value.get('history')


def init(custom_prompt_path: str | PathLike):
    global CUSTOM_PROMPT_PATH
    CUSTOM_PROMPT_PATH = custom_prompt_path
    load_custom_history()
    return True


def read_danmaku() -> Danmaku | None:
    """
    从连接成功的直播间中按照一定的规则抽取弹幕。
    当没有弹幕可以被抽取时，返回 None.
    :return: 弹幕对象 | None
    """
    danmaku = bili_serv.select_01(k=3)
    if danmaku:
        logger.info(f'✅ [{danmaku.username}]({danmaku.uid}) {danmaku.msg}')
    return danmaku


def read_screen() -> str | None:
    """
    从指定窗口中读取截图并返回一段英文描述。
    当没有成功截图是，返回 None.
    :return:
    """
    img = scrn_serv.screen_cap()
    screen_desc = blip_serv.infer(img) if img else None
    logger.info(f'👀 {screen_desc}')
    return screen_desc


@dataclass
class GameEvent:
    health: int
    food: int


def convert_2_query(danmaku: Danmaku, screen_desc: str, game_event: GameEvent):
    query = {
        "弹幕": {
            "用户名": danmaku.username,
            "内容": danmaku.msg
        } if danmaku else 'None',
        "游戏画面": f'{screen_desc}' if screen_desc else 'None',
        "游戏状态": {
            "生命值": game_event.health,
            "饥饿值": game_event.food
        }
    }
    # if danmaku and screen_desc:
    #     query = {
    #         danmaku.username: danmaku.msg,
    #         "screen": screen_desc
    #     }
    # elif screen_desc and not danmaku:
    #     query = {
    #         "screen": screen_desc
    #     }
    # elif not screen_desc and danmaku:
    #     query = {
    #         danmaku.username: danmaku.msg
    #     }
    # else:
    #     query = None
    if query:
        return str(json.dumps(obj=query, indent=4, ensure_ascii=False))
    return None


def tts_with_tone(sentence: str):
    """
    自动分析句子语气，并合成语音
    :param sentence: 将要被合成的文本
    :return: 语气，合成语音的路径
    """
    # 利用 LLM 分析句子语气
    tone = tone_serv.analyze_tone(sentence)

    # 根据语气切换 TTS 的提示合成对应的语音
    wav_file_path = gptsovits_serv.predict_with_prompt(text_language=LANG, text=sentence,
                                                       refer_wav_path=tone.refer_wav_path,
                                                       prompt_text=tone.prompt_text,
                                                       prompt_language=tone.prompt_language)
    return tone, wav_file_path


def read_game_event():
    return GameEvent(health=20, food=20)


async def life_circle(add_audio_event: threading.Event):
    global HISTORY, LANG

    # 尝试抽取弹幕
    danmaku = read_danmaku()

    # 尝试截图识别内容
    screen_desc = read_screen()

    # 尝试获取游戏事件
    game_event = read_game_event()

    # 将上述获取的信息转化为对话的请求
    query = convert_2_query(danmaku, screen_desc, game_event)

    if query is None or query == '':
        logger.debug('生命周期提前结束')
        return

    logger.info(query)

    # 其中 resp
    # 第1轮循环 resp = '我'
    # 第2轮循环 resp = '我是'
    # 第3轮循环 resp = '我是一个'
    # 第4轮循环 resp = '我是一个机器'
    # 第5轮循环 resp = '我是一个机器人'
    # 第6轮循环 resp = '我是一个机器人。'
    # ... 以此类推

    last_split_idx = 0

    async for response, history in chatglm3.api.stream_predict(query=query, history=HISTORY, top_p=1., temperature=1.):
        if not response or response[-1] not in ['。', '！', '？', '!', '?']:
            continue

        sentence = response[last_split_idx:]
        last_split_idx = len(response)

        if is_blank(sentence):
            continue

        # 更新 LLM 会话历史
        HISTORY = history

        # 自动语气语音合成
        tone, wav_file_path = tts_with_tone(sentence)

        logger.info(f'🗒️ 历史记录：{len(HISTORY)} \n💖 语气：{tone.id} \n💭 {sentence}')

        if not wav_file_path:
            logger.warning(f'❕ 这条语音未能合成：{sentence}')
            break

        obs_serv.write_output(danmaku, sentence, tone)

        # 播放语音
        audio_player.service.add_audio(wav_file_path, sentence)
        add_audio_event.set()
