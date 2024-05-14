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
    global _max_history, _waiting_interval, _role_play_template_path, _memory

    _max_history = 40
    _waiting_interval = 2

    _memory = None


async def update():
    try_reset_memory()

    # 尝试读取语音 | 抽取弹幕 | 截图识别 | 获取游戏事件
    transcript = fusion_pipeline.hear()
    danmaku = fusion_pipeline.danmaku()
    screen_desc = fusion_pipeline.see()
    game_event = fusion_pipeline.minecraft_event()

    # 将上述获取的信息转化为对话的请求
    query = fusion_pipeline.merge(transcript=transcript, danmaku=danmaku, screen_desc=screen_desc,
                                  game_event=game_event)

    assert query and query != '', '生命周期提前结束，因为没有足够的信息进行综合推理'

    _memory.text = query
    logger.info(query)

    if danmaku:
        obs.api.write_danmaku_output(danmaku)

    # 注意这里, 开发者说的话会覆盖弹幕
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

        # 播放语音
        if wav_file_path:
            audio_player.service.add_audio(wav_file_path, sentence)

    # 推理后更新历史
    memory.history = ret_llm_response.history


async def start():
    logger.info('💜 Zerolan Live Robot 启动！')
    while True:
        try:
            await update()
        except AssertionError as e:
            logger.warning(f"{e}")
        await asyncio.sleep(_waiting_interval)


def try_reset_memory(force: bool = False):
    global _memory

    # 避免 bot 因为阻塞而停止运行
    if force:
        _memory = fusion_pipeline.load_history()
    elif not _memory:
        _memory = fusion_pipeline.load_history()
    elif len(_memory.history) > _max_history:
        _memory = fusion_pipeline.load_history()


def memory():
    return copy.deepcopy(_memory)
