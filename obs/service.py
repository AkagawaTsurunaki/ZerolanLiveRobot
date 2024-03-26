from loguru import logger

from utils.datacls import Danmaku
from tone_ana.service import Tone

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


def write_llm_output(text):
    with open(file=LLM_OUTPUT_PATH, mode='w+', encoding='utf-8') as file:
        file.write(f'{text}')


def write_tone_output(tone: Tone):
    with open(file=TONE_OUTPUT_PATH, mode='w+', encoding='utf-8') as file:
        file.write(tone.id)


def write_danmaku_output(danmaku):
    with open(file=DANMAKU_OUTPUT_PATH, mode='w+', encoding='utf-8') as file:
        if danmaku:
            file.write(f'{danmaku.username} 说: {danmaku.msg}')


# def write_output(danmaku: Danmaku, text: str, tone: Tone):
#     """
#     将获取到的弹幕，LLM 输出的文本，和文本所蕴含的情感写入 OBS 字幕文件中。
#     :param danmaku: 弹幕对象
#     :param text: LLM 输出的文本字符串
#     :param tone: 语气对象
#     """
#     with open(file=TONE_OUTPUT_PATH, mode='w+', encoding='utf-8') as file:
#         file.write(tone.id)
#     with open(file=LLM_OUTPUT_PATH, mode='w+', encoding='utf-8') as file:
#         file.write(f'{text}')
#     with open(file=DANMAKU_OUTPUT_PATH, mode='w+', encoding='utf-8') as file:
#         if danmaku:
#             file.write(f'{danmaku.username} 说: {danmaku.msg}')
