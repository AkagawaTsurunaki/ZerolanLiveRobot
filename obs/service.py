from loguru import logger

from tone_ana.service import Tone
from utils.datacls import Danmaku

DANMAKU_OUTPUT_PATH: str
TONE_OUTPUT_PATH: str
LLM_OUTPUT_PATH: str

IS_INITIALIZE = False


def init(danmaku_output_path, tone_output_path, llm_output_path):
    logger.info('😀 OBS 服务初始化中……')
    global DANMAKU_OUTPUT_PATH, TONE_OUTPUT_PATH, LLM_OUTPUT_PATH, IS_INITIALIZE
    DANMAKU_OUTPUT_PATH = danmaku_output_path
    TONE_OUTPUT_PATH = tone_output_path
    LLM_OUTPUT_PATH = llm_output_path
    IS_INITIALIZE = True
    logger.info('😀 OBS 服务初始化完毕')
    return IS_INITIALIZE


def write_llm_output(text: str | None):
    with open(file=LLM_OUTPUT_PATH, mode='w+', encoding='utf-8') as file:
        file.write(f'{text}' if text else '')


def write_tone_output(tone: Tone | None):
    with open(file=TONE_OUTPUT_PATH, mode='w+', encoding='utf-8') as file:
        file.write(tone.id if tone else '')


def write_danmaku_output(danmaku: Danmaku | None):
    with open(file=DANMAKU_OUTPUT_PATH, mode='w+', encoding='utf-8') as file:
        file.write(f'{danmaku.username} 说: {danmaku.msg}' if danmaku else '')
