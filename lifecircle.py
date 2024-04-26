import asyncio
import json
from typing import Final

from loguru import logger

import initzr
import minecraft.app
import obs.api
from asr.service import ASRService
from audio_player.service import AudioPlayerService
from img_cap.pipeline import ImageCapPipeline, ImageCapQuery
from livestream.pipeline import LiveStreamPipeline
from llm.pipeline import LLMPipeline
from minecraft.app import GameEvent
from scrnshot import api as scrn_serv
from tone_ana import api as tone_serv
from tts.gptsovits import api as gptsovits_serv
from utils import util
from utils.datacls import Danmaku, LLMQuery, Chat, Role
from utils.util import is_blank

LANG = 'zh'

DEV_NAME: Final[str] = '赤川鹤鸣'
LLM_PIPELINE = LLMPipeline()
LIVE_STREAM_PIPELINE = LiveStreamPipeline()
MAX_HISTORY = 40
# Configuration of Zerolan Live Robot
CONFIG = initzr.load_zerolan_live_robot_config()

# Current history
memory: LLMQuery | None = None


def load_history():
    template = util.read_yaml(CONFIG.role_play_template_path)
    format = json.dumps(template['format'], ensure_ascii=False, indent=4)

    # Assign history
    history: list[Chat] = []
    for chat in template['history']:
        if isinstance(chat, dict):
            content = json.dumps(chat, ensure_ascii=False, indent=4)
            history.append(Chat(role=Role.USER, content=content))
        elif isinstance(chat, str):
            history.append(Chat(role=Role.ASSISTANT, content=chat))

    # Assign system prompt
    for chat in history:
        chat.content = chat.content.replace('${format}', format)

    return LLMQuery(text='', history=history)


def try_reset_memory(force: bool = False):
    global memory
    # Prevent bot from slow-calculation block for too long
    if force:
        memory = load_history()
    elif not memory:
        memory = load_history()
    elif len(memory.history) > MAX_HISTORY:
        memory = load_history()


def read_danmaku() -> Danmaku | None:
    """
    从连接成功的直播间中按照一定的规则抽取弹幕。
    当没有弹幕可以被抽取时，返回 None.
    :return: 弹幕对象 | None
    """
    danmaku = LIVE_STREAM_PIPELINE.read_danmaku_latest_longest(k=3)
    if danmaku:
        logger.info(f'✅ [{danmaku.username}]({danmaku.uid}) {danmaku.msg}')
    return danmaku


def read_screen(img_cap_pipeline: ImageCapPipeline) -> str | None:
    """
    从指定窗口中读取截图并返回一段英文描述。
    当没有成功截图是，返回 None.
    :return:
    """
    img_save_path = scrn_serv.screen_cap()
    if img_save_path:
        caption = img_cap_pipeline.predict(ImageCapQuery(img_path=img_save_path, prompt='There'))
        return caption
    return None


def read_from_microphone(asr_serv: ASRService) -> str | None:
    transcript = asr_serv.select_latest_unread()

    if transcript:
        logger.info(f'🎙️ 用户语音输入：{transcript}')
    return transcript


def convert_2_query(transcript: str, danmaku: Danmaku, screen_desc: str, game_event: GameEvent) -> str | None:
    query = {}

    if transcript:
        query['开发者说'] = transcript
    if danmaku:
        query['弹幕'] = {
            "用户名": danmaku.username,
            "内容": danmaku.msg
        }

    if screen_desc:
        query['游戏画面'] = f'{screen_desc}'

    if game_event:
        query['游戏状态'] = {
            "生命值": game_event.health,
            "饥饿值": game_event.food,
            "环境": game_event.description
        }
    if query:
        query = str(json.dumps(obj=query, indent=4, ensure_ascii=False))
        query = f'```\n{query}\n```'
        return query
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
    obs.api.write_tone_output(tone)

    return tone, wav_file_path


def read_game_event():
    return minecraft.app.select01()


async def life_circle(audio_player_service: AudioPlayerService,
                      asr_service: ASRService,
                      img_cap_pipeline: ImageCapPipeline
                      ):
    global LANG, memory

    try_reset_memory()

    # 尝试读取语音 | 抽取弹幕 | 截图识别 | 获取游戏事件
    transcript = read_from_microphone(asr_service)
    danmaku = read_danmaku()
    screen_desc = read_screen(img_cap_pipeline)
    game_event = read_game_event()

    # 将上述获取的信息转化为对话的请求
    query = convert_2_query(transcript, danmaku, screen_desc, game_event)

    if query is None or query == '':
        logger.warning('生命周期提前结束')
        return

    memory.text = query
    logger.info(query)

    # 注意这里, 开发者说的话会覆盖弹幕
    if danmaku:
        obs.api.write_danmaku_output(danmaku)

    if transcript:
        obs.api.write_voice_input(DEV_NAME, transcript)

    last_split_idx = 0

    ret_llm_response = None

    async for llm_response in LLM_PIPELINE.stream_predict(memory):
        ret_llm_response = llm_response
        response = llm_response.response
        if not response or response[-1] not in ['。', '！', '？', '!', '?']:
            continue

        sentence = response[last_split_idx:]
        last_split_idx = len(response)

        if is_blank(sentence):
            continue

        # 自动语气语音合成
        tone, wav_file_path = tts_with_tone(sentence)

        logger.info(f'🗒️ 历史记录：{len(llm_response.history)} \n💖 语气：{tone.id} \n💭 {sentence}')

        if not wav_file_path:
            logger.warning(f'❕ 这条语音未能合成：{sentence}')
            break

        # 播放语音
        audio_player_service.add_audio(wav_file_path, sentence)

    memory.history = ret_llm_response.history


async def start_cycle(ap_serv: AudioPlayerService, asr_serv: ASRService, img_cap_pipeline: ImageCapPipeline):
    logger.info('💜 ZerolanLiveRobot，启动！')
    while True:
        await life_circle(audio_player_service=ap_serv,
                          asr_service=asr_serv,
                          img_cap_pipeline=img_cap_pipeline
                          )
        await asyncio.sleep(2)
