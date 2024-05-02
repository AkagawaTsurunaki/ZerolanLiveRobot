import asyncio
import copy
import json

from loguru import logger

import audio_player.service
import minecraft.app
import obs.api
import scrnshot.service
import tone_ana.service
import zio.util
from common import util
from common.datacls import Danmaku
from common.util import is_blank
from zio.util import write_wav
from config import GLOBAL_CONFIG as G_CFG
from img_cap.pipeline import ImageCapPipeline, ImageCaptioningModelQuery
from livestream.pipeline import LiveStreamPipeline
from llm.pipeline import LLMPipeline, LLMQuery, Role, Chat
from minecraft.app import GameEvent
from tts.pipeline import TTSPipeline, TTSQuery
import asr.service

_lang: str
_dev_name: str
_max_history: int
_waiting_interval: int

_role_play_template_path: str
_memory: LLMQuery | None

_llm_pipeline: LLMPipeline
_live_stream_pipeline: LiveStreamPipeline
_img_cap_pipeline: ImageCapPipeline
_tts_pipeline: TTSPipeline


def init():
    global _lang, _dev_name, _max_history, _waiting_interval, _role_play_template_path, \
        _memory, _llm_pipeline, _live_stream_pipeline, _img_cap_pipeline, _tts_pipeline

    _lang: str = 'zh'
    _dev_name: str = 'AkagawaTsurunaki'
    _max_history: int = 40
    _waiting_interval: int = 2

    _role_play_template_path = G_CFG.zerolan_live_robot_config.role_play_template_path
    _memory: LLMQuery | None = None
    # Pipelines
    _llm_pipeline = LLMPipeline(G_CFG)
    _live_stream_pipeline = LiveStreamPipeline(G_CFG)
    _img_cap_pipeline = ImageCapPipeline(G_CFG)
    _tts_pipeline = TTSPipeline(G_CFG)


async def update():
    try_reset_memory()

    # 尝试读取语音 | 抽取弹幕 | 截图识别 | 获取游戏事件
    transcript = read_from_microphone()
    danmaku = read_danmaku()
    screen_desc = read_screen()
    game_event = read_game_event()

    # 将上述获取的信息转化为对话的请求
    query = convert_2_query(transcript, danmaku, screen_desc, game_event)

    if query is None or query == '':
        logger.warning('生命周期提前结束')
        return

    _memory.text = query
    logger.info(query)

    # 注意这里, 开发者说的话会覆盖弹幕
    if danmaku:
        obs.api.write_danmaku_output(danmaku)

    if transcript:
        obs.api.write_voice_input(transcript)

    last_split_idx = 0

    ret_llm_response = None

    async for llm_response in _llm_pipeline.stream_predict(_memory):
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
        audio_player.service.add_audio(wav_file_path, sentence)

    memory.history = ret_llm_response.history


async def start():
    logger.info('Zerolan Live Robot Starting!')
    while True:
        await update()
        await asyncio.sleep(_waiting_interval)


def load_history():
    template = zio.util.read_yaml(_role_play_template_path)
    fmt = json.dumps(template['format'], ensure_ascii=False, indent=4)

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
        chat.content = chat.content.replace('${format}', fmt)

    return LLMQuery(text='', history=history)


def try_reset_memory(force: bool = False):
    global _memory

    # Prevent bot from slow-calculation block for too long
    if force:
        _memory = load_history()
    elif not _memory:
        _memory = load_history()
    elif len(_memory.history) > _max_history:
        _memory = load_history()


def read_danmaku() -> Danmaku | None:
    danmaku = _live_stream_pipeline.read_danmaku_latest_longest(k=3)
    if danmaku:
        logger.info(f'✅ [{danmaku.username}]({danmaku.uid}) {danmaku.msg}')
    return danmaku


def read_screen() -> str | None:
    img_save_path = scrnshot.service.screen_cap()
    if img_save_path:
        caption = _img_cap_pipeline.predict(ImageCaptioningModelQuery(img_path=img_save_path, prompt='There'))
        return caption
    return None


def read_from_microphone() -> str | None:
    transcript = asr.service.select_latest_unread()

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
    # 利用 LLM 分析句子语气
    tone = tone_ana.service.analyze_tone(sentence)

    # 根据语气切换 TTS 的提示合成对应的语音
    tts_query = TTSQuery(text=sentence, text_language=_lang, refer_wav_path=tone.refer_wav_path,
                         prompt_text=tone.prompt_text, prompt_language=tone.prompt_language)
    tts_response = _tts_pipeline.predict(tts_query)
    wav_file_path = write_wav(tts_response.wave_data)
    obs.api.write_tone_output(tone)

    return tone, wav_file_path


def read_game_event():
    return minecraft.app.mark_last_event_as_read_and_clear_list()


def memory():
    return copy.deepcopy(_memory)
