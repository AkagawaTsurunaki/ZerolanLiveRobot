import asyncio
import copy
import json

from loguru import logger

import minecraft.app
import obs.api
from asr.service import ASRService
from audio_player.service import AudioPlayerService
from config import GlobalConfig
from img_cap.pipeline import ImageCapPipeline, ImageCapQuery
from livestream.pipeline import LiveStreamPipeline
from llm.pipeline import LLMPipeline
from minecraft.app import GameEvent
from scrnshot import api as scrn_serv
from tone_ana import api as tone_serv
from tts.pipeline import TTSPipeline, TTSQuery
from utils import util
from utils.datacls import Danmaku, LLMQuery, Chat, Role
from utils.util import is_blank, write_wav


class LifeCycle:
    def __init__(self, cfg: GlobalConfig, asr_service: ASRService, audio_player_service: AudioPlayerService):
        self._lang: str = 'zh'
        self._dev_name: str = 'AkagawaTsurunaki'
        self._max_history: int = 40
        self._waiting_interval: int = 2

        self._role_play_template_path = cfg.zerolan_live_robot_config.role_play_template_path
        self._memory: LLMQuery | None = None
        # Pipelines
        self._llm_pipeline = LLMPipeline(cfg)
        self._live_stream_pipeline = LiveStreamPipeline(cfg)
        self._img_cap_pipeline = ImageCapPipeline(cfg)
        self._tts_pipeline = TTSPipeline(cfg)
        # Services
        self._asr_service = asr_service
        self._audio_player_service = audio_player_service

    async def update(self):

        self.try_reset_memory()

        # 尝试读取语音 | 抽取弹幕 | 截图识别 | 获取游戏事件
        transcript = self.read_from_microphone()
        danmaku = self.read_danmaku()
        screen_desc = self.read_screen()
        game_event = self.read_game_event()

        # 将上述获取的信息转化为对话的请求
        query = self.convert_2_query(transcript, danmaku, screen_desc, game_event)

        if query is None or query == '':
            logger.warning('生命周期提前结束')
            return

        self._memory.text = query
        logger.info(query)

        # 注意这里, 开发者说的话会覆盖弹幕
        if danmaku:
            obs.api.write_danmaku_output(danmaku)

        if transcript:
            obs.api.write_voice_input(self._dev_name, transcript)

        last_split_idx = 0

        ret_llm_response = None

        async for llm_response in self._llm_pipeline.stream_predict(self._memory):
            ret_llm_response = llm_response
            response = llm_response.response
            if not response or response[-1] not in ['。', '！', '？', '!', '?']:
                continue

            sentence = response[last_split_idx:]
            last_split_idx = len(response)

            if is_blank(sentence):
                continue

            # 自动语气语音合成
            tone, wav_file_path = self.tts_with_tone(sentence)

            logger.info(f'🗒️ 历史记录：{len(llm_response.history)} \n💖 语气：{tone.id} \n💭 {sentence}')

            if not wav_file_path:
                logger.warning(f'❕ 这条语音未能合成：{sentence}')
                break

            # 播放语音
            self._audio_player_service.add_audio(wav_file_path, sentence)

        self.memory.history = ret_llm_response.history

    async def start(self):
        logger.info('Zerolan Live Robot Starting!')
        while True:
            await self.update()
            await asyncio.sleep(self._waiting_interval)

    def load_history(self):
        template = util.read_yaml(self._role_play_template_path)
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

    def try_reset_memory(self, force: bool = False):
        # Prevent bot from slow-calculation block for too long
        if force:
            self.memory = self.load_history()
        elif not self.memory:
            self.memory = self.load_history()
        elif len(self.memory.history) > self._max_history:
            self.memory = self.load_history()

    def read_danmaku(self) -> Danmaku | None:
        danmaku = self._live_stream_pipeline.read_danmaku_latest_longest(k=3)
        if danmaku:
            logger.info(f'✅ [{danmaku.username}]({danmaku.uid}) {danmaku.msg}')
        return danmaku

    def read_screen(self) -> str | None:
        img_save_path = scrn_serv.screen_cap()
        if img_save_path:
            caption = self._img_cap_pipeline.predict(ImageCapQuery(img_path=img_save_path, prompt='There'))
            return caption
        return None

    def read_from_microphone(self) -> str | None:
        transcript = self._asr_service.select_latest_unread()

        if transcript:
            logger.info(f'🎙️ 用户语音输入：{transcript}')
        return transcript

    @staticmethod
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

    def tts_with_tone(self, sentence: str):
        # 利用 LLM 分析句子语气
        tone = tone_serv.analyze_tone(sentence)

        # 根据语气切换 TTS 的提示合成对应的语音
        tts_query = TTSQuery(text=sentence, text_language=self._lang, refer_wav_path=tone.refer_wav_path,
                             prompt_text=tone.prompt_text, prompt_language=tone.prompt_language)
        tts_response = self._tts_pipeline.predict(tts_query)
        wav_file_path = write_wav(tts_response.wave_data)
        obs.api.write_tone_output(tone)

        return tone, wav_file_path

    def read_game_event(self):
        return minecraft.app.select01()

    def memory(self):
        return copy.deepcopy(self._memory)
