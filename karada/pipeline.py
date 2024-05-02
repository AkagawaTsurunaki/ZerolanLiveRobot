import json

from loguru import logger

import asr.service
import minecraft.app
import scrnshot.api
import tone_ana.service
import zio.util
from common.datacls import Transcript, Danmaku, TTSQuery, Chat, Role, LLMQuery
from config import GLOBAL_CONFIG as G_CFG
from img_cap.pipeline import ImageCapPipeline, ImageCaptioningModelQuery
from livestream.pipeline import LiveStreamPipeline
from llm.pipeline import LLMPipeline
from minecraft.app import GameEvent
from tts.pipeline import TTSPipeline
from zio.writer import Writer


class FusionPipeline:
    def __init__(self):
        self.llm_pipeline = LLMPipeline(G_CFG)
        self._live_stream_pipeline = LiveStreamPipeline(G_CFG)
        self._img_cap_pipeline = ImageCapPipeline(G_CFG)
        self._tts_pipeline = TTSPipeline(G_CFG)
        self._lang = G_CFG.zerolan_live_robot_config.lang
        self._role_play_template_path = G_CFG.zerolan_live_robot_config.role_play_template_path
        self.wav_writer = Writer(G_CFG.text_to_speech.save_directory)

    def see(self) -> str | None:
        img_save_path = scrnshot.api.screen_cap()
        if img_save_path:
            query = ImageCaptioningModelQuery(img_path=img_save_path, prompt='There')
            caption = self._img_cap_pipeline.predict(query)
            return caption.caption
        return None

    def hear(self) -> Transcript | None:
        transcript = asr.service.select_latest_unread()
        if transcript:
            logger.info(f'🎙️ User voice: {transcript}')
        return transcript

    def danmaku(self) -> Danmaku | None:
        danmaku = self._live_stream_pipeline.read_danmaku_latest_longest(k=3)
        if danmaku:
            logger.info(f'✅ [{danmaku.username}]({danmaku.uid}) {danmaku.msg}')
        return danmaku

    def minecraft_event(self):
        return minecraft.app.mark_last_event_as_read_and_clear_list()

    def merge(self,
              transcript: Transcript,
              danmaku: Danmaku,
              screen_desc: str,
              game_event: GameEvent) -> str | None:
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

    def tts_with_tone(self, sentence: str):
        # 利用 LLM 分析句子语气
        tone = tone_ana.service.analyze_tone(sentence)

        # 根据语气切换 TTS 的提示合成对应的语音
        tts_query = TTSQuery(text=sentence, text_language=self._lang, refer_wav_path=tone.refer_wav_path,
                             prompt_text=tone.prompt_text, prompt_language=tone.prompt_language)
        tts_response = self._tts_pipeline.predict(tts_query)
        wav_file_path = self.wav_writer.write_wav(tts_response.wave_data)

        return tone, wav_file_path

    def load_history(self):
        template = zio.util.read_yaml(self._role_play_template_path)
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
