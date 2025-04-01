import asyncio

from loguru import logger
from zerolan.data.pipeline.asr import ASRStreamQuery
from zerolan.data.pipeline.tts import TTSQuery

from common.enumerator import Language
from common.io.api import save_audio
from common.concurrent.killable_thread import KillableThread
from common.utils.str_util import split_by_punc
from event.event_data import SpeechEvent
from event.event_emitter import emitter
from event.registry import EventKeyRegistry
from manager.config_manager import get_config
from manager.tts_prompt_manager import TTSPromptManager
from services.playground.bridge import PlaygroundBridge
from services.playground.data import Arg_MenuItem
from services.res_server import ResourceServer
from ump.pipeline.asr import ASRPipeline
from ump.pipeline.tts import TTSPipeline

_config = get_config()


class RestaurantBot:
    def __init__(self):
        super().__init__()
        self.live2d_model = _config.service.playground.model_dir
        self._playground = PlaygroundBridge(_config.service.playground)
        self._res_server = ResourceServer(_config.service.res_server.host,
                                          _config.service.res_server.port, )

        self._asr = ASRPipeline(_config.pipeline.asr)
        self._tts = TTSPipeline(_config.pipeline.tts)
        self.tts_prompt_manager = TTSPromptManager(_config.character.speech)
        self.bot_id = _config.character.bot_name
        self.bot_name = _config.character.bot_name
        self._scripts = [
            "那就让美食扫除您的坏心情吧！今天本店为您推荐这些好吃的甜品哦！",
            "当然可以。有以下菜品可以选择。",
            "好的，已经为您下单！您是8号桌，水果拼盘正在制作中，本店为您送上一天的好心情。"
        ]
        self._p = 0

        self.init()

    async def start(self):

        self.threads = []
        thread = KillableThread(target=self._playground.start, daemon=True)
        thread2 = KillableThread(target=self._res_server.start, daemon=True)
        thread.start()
        thread2.start()
        self.threads.append(thread)
        self.threads.append(thread2)

        async with asyncio.TaskGroup() as tg:
            tg.create_task(emitter.start())

    def init(self):
        @emitter.on(EventKeyRegistry.Playground.PLAYGROUND_CONNECTED)
        def on_playground_connected(_):
            self._playground.load_live2d_model(
                bot_id=self.bot_id,
                bot_display_name=self.bot_name,
                model_dir=self.live2d_model
            )
            logger.info(f"Live 2D model loaded: {self.live2d_model}")

        @emitter.on(EventKeyRegistry.Device.SERVICE_VAD_SPEECH_CHUNK)
        def handle_asr(event: SpeechEvent):
            speech, channels, sample_rate = event.speech, event.channels, event.sample_rate
            query = ASRStreamQuery(is_final=True, audio_data=speech, channels=channels, sample_rate=sample_rate,
                                   media_type=event.audio_type)
            for prediction in self._asr.stream_predict(query):
                logger.info(f"ASR: {prediction.transcript}")
                self._playground.show_user_input_text(prediction.transcript)
                if self._p > 2:
                    return
                content = self._scripts[self._p]
                if "今天" in prediction.transcript:
                    self.play_tts(content)
                    self._p += 1
                    menu_list = [
                        Arg_MenuItem(img_path="resources/static/image/提拉米苏.jpg", text="提拉米苏"),
                        Arg_MenuItem(img_path="resources/static/image/布朗尼.jpg", text="布朗尼"),
                        Arg_MenuItem(img_path="resources/static/image/芭菲.jpg", text="芭菲")
                    ]
                    self._playground.show_menu(menu_list)
                elif "清淡" in prediction.transcript:
                    self.play_tts(content)
                    self._p += 1
                    menu_list = [
                        Arg_MenuItem(img_path="resources/static/image/缤纷水果拼盘.jpg", text="缤纷水果拼盘"),
                        Arg_MenuItem(img_path="resources/static/image/千岛水果沙拉.jpg", text="千岛水果沙拉"),
                        Arg_MenuItem(img_path="resources/static/image/银耳莲子羹.jpg", text="银耳莲子羹")
                    ]
                    self._playground.show_menu(menu_list)
                elif "水果" in prediction.transcript:
                    self.play_tts(content)
                    self._p += 1

    def play_tts(self, text: str):
        tts_prompt = self.tts_prompt_manager.default_tts_prompt
        transcripts = split_by_punc(text, Language.ZH)
        self._playground.add_history(role="assistant", text=text, username=self.bot_name)
        for idx, transcript in enumerate(transcripts):
            query = TTSQuery(
                text=transcript,
                text_language=Language.ZH,
                refer_wav_path=tts_prompt.audio_path,
                prompt_text=tts_prompt.prompt_text,
                prompt_language=tts_prompt.lang,
                audio_type="wav"
            )
            prediction = self._tts.predict(query=query)
            logger.info(f"TTS: {query.text}")
            audio_path = save_audio(wave_data=prediction.wave_data, prefix='tts')
            self._playground.play_speech(bot_id=self.bot_id, audio_path=audio_path,
                                         transcript=transcript, bot_name=self.bot_name)

    def join(self):
        for thread in self.threads:
            thread.join()
