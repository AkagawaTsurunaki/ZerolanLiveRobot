import asyncio
import copy

from loguru import logger

import audio_player.service
import obs.api
from common.datacls import LLMQuery
from common.util import is_blank
from karada.pipeline import FusionPipeline

_max_history: int
_waiting_interval: int

_role_play_template_path: str
_memory: LLMQuery | None

fusion_pipeline = FusionPipeline()


def init():
    global _max_history, _waiting_interval, _role_play_template_path, \
        _memory

    _max_history = 40
    _waiting_interval = 2

    _memory = None
    # Pipelines


async def update():
    try_reset_memory()

    # 尝试读取语音 | 抽取弹幕 | 截图识别 | 获取游戏事件
    transcript = fusion_pipeline.hear()
    danmaku = fusion_pipeline.danmaku()
    screen_desc = fusion_pipeline.see()
    game_event = fusion_pipeline.minecraft_event()

    # 将上述获取的信息转化为对话的请求
    query = fusion_pipeline.merge(transcript=transcript, danmaku=danmaku, screen_desc=screen_desc, game_event=game_event)

    if query is None or query == '':
        logger.warning('生命周期提前结束')
        return

    _memory.text = query
    logger.info(query)

    # 注意这里, 开发者说的话会覆盖弹幕
    if danmaku:
        obs.api.write_danmaku_output(danmaku)

    if transcript:
        obs.api.write_voice_input(transcript.content)

    last_split_idx = 0

    ret_llm_response = None

    async for llm_response in fusion_pipeline.llm_pipeline.stream_predict(_memory):
        ret_llm_response = llm_response
        response = llm_response.response
        if not response or response[-1] not in ['。', '！', '？', '!', '?']:
            continue

        sentence = response[last_split_idx:]
        last_split_idx = len(response)

        if is_blank(sentence):
            continue

        # 自动语气语音合成
        tone, wav_file_path = fusion_pipeline.tts_with_tone(sentence)
        obs.api.write_tone_output(tone)

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


def try_reset_memory(force: bool = False):
    global _memory

    # Prevent bot from slow-calculation block for too long
    if force:
        _memory = fusion_pipeline.load_history()
    elif not _memory:
        _memory = fusion_pipeline.load_history()
    elif len(_memory.history) > _max_history:
        _memory = fusion_pipeline.load_history()


def memory():
    return copy.deepcopy(_memory)
