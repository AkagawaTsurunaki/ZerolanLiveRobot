import initzr
from utils.datacls import Danmaku, Tone

CONFIG = initzr.load_obs_config()
DANMAKU_OUTPUT_PATH = CONFIG.danmaku_output_path
TONE_OUTPUT_PATH = CONFIG.tone_output_path
LLM_OUTPUT_PATH = CONFIG.llm_output_path


def write_llm_output(text: str | None):
    with open(file=LLM_OUTPUT_PATH, mode='w+', encoding='utf-8') as file:
        file.write(f'{text}' if text else '')


def write_tone_output(tone: Tone | None):
    with open(file=TONE_OUTPUT_PATH, mode='w+', encoding='utf-8') as file:
        file.write(tone.id if tone else '')


def write_danmaku_output(danmaku: Danmaku | None):
    with open(file=DANMAKU_OUTPUT_PATH, mode='w+', encoding='utf-8') as file:
        file.write(f'{danmaku.username} 说: {danmaku.msg}' if danmaku else '')


def write_voice_input(who: str, transcript: str):
    with open(file=DANMAKU_OUTPUT_PATH, mode='w+', encoding='utf-8') as file:
        file.write(f'{who} 说: {transcript}')
