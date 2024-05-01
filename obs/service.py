from config import GlobalConfig
from zio.writer import Writer
from common.datacls import Danmaku, Tone


class ObsService:
    def __init__(self, cfg: GlobalConfig):
        self._writer_4_llm = Writer(cfg.obs.llm_output_path)
        self._writer_4_danmaku = Writer(cfg.obs.danmaku_output_path)
        self._writer_4_tone = Writer(cfg.obs.tone_output_path)

    def clear_output(self):
        self._writer_4_danmaku.write('')

    def write_danmaku_output(self, danmaku: Danmaku | None):
        content = f'{danmaku.username}: {danmaku.msg}' if danmaku else ''
        self._writer_4_danmaku.write(content)

    def write_tone_output(self, tone: Tone):
        content = tone.id
        self._writer_4_tone.write(content)

    def write_voice_input(self, transcript: str):
        self._writer_4_llm.write(transcript)

    def write_llm_output(self, text: str):
        self._writer_4_danmaku.write(text)
