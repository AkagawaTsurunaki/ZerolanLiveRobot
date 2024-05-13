from common.datacls import Danmaku, Tone
from zio.writer import Writer
from config import GLOBAL_CONFIG as G_CFG

_writer_4_llm = Writer(G_CFG.obs.llm_output_path)
_writer_4_danmaku = Writer(G_CFG.obs.danmaku_output_path)
_writer_4_tone = Writer(G_CFG.obs.tone_output_path)


def clear_output():
    _writer_4_danmaku.write_str('')


def write_danmaku_output(danmaku: Danmaku | None):
    content = f'{danmaku.username}: {danmaku.msg}' if danmaku else ''
    _writer_4_danmaku.write_str(content)


def write_tone_output(tone: Tone):
    content = tone.id
    _writer_4_tone.write_str(content)


def write_voice_input(transcript: str):
    _writer_4_llm.write_str(transcript)


def write_llm_output(text: str):
    _writer_4_danmaku.write_str(text)
