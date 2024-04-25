from dataclasses import dataclass
from typing import List

import utils.util

@dataclass
class ...

@dataclass
class LiveStreamConfig:
    enable: bool = True
    platforms: List[dict] = None


@dataclass
class ScreenshotConfig:
    enable: bool = True
    window_title: str = "Minecraft"
    k: float = 0.9
    save_directory: str = ".tmp/screenshots"


@dataclass
class ImageCaptioningConfig:
    enable: bool = True
    debug: bool = False
    host: str = "127.0.0.1"
    port: int = 9879
    models: List[dict] = None


@dataclass
class TextToSpeechConfig:
    enable: bool = True
    debug: bool = False
    host: str = "127.0.0.1"
    port: int = 9880
    save_directory: str = ".tmp/wav_output"
    models: List[dict] = None


@dataclass
class LargeLanguageModelConfig:
    enable: bool = True
    debug: bool = False
    host: str = "127.0.0.1"
    port: int = 9881
    models: List[dict] = None


@dataclass
class ToneAnalysisConfig:
    enable: bool = True
    tone_analysis_template_path: str = "template/my_tone_ayalysis_template.yaml"


@dataclass
class OBSConfig:
    enable: bool = True
    danmaku_output_path: str = ".tmp/danmaku_output/output.txt"
    tone_output_path: str = ".tmp/tone_output/output.txt"
    llm_output_path: str = ".tmp/llm_output/output.txt"


@dataclass
class VADConfig:
    enable: bool = True
    save_dir: str = ".tmp/records"
    chunk: int = 4096
    sample_rate: int = 16000
    threshold: int = 600
    max_mute_count: int = 10


@dataclass
class ASRConfig:
    enable: bool = True
    debug: bool = False
    host: str = "127.0.0.1"
    port: int = 9882
    models: List[dict] = None


@dataclass
class ZerolanLiveRobotConfig:
    enable: bool = True
    debug: bool = False
    host: str = "127.0.0.1"
    port: int = 9888
    role_play_template_path: str = "template/role_play_template_short.yaml"


@dataclass
class MinecraftConfig:
    enable: bool = True


@dataclass
class GlobalConfig:
    live_stream: LiveStreamConfig
    screenshot: ScreenshotConfig
    image_captioning: ImageCaptioningConfig
    text_to_speech: TextToSpeechConfig
    large_language_model: LargeLanguageModelConfig
    tone_analysis: ToneAnalysisConfig
    obs: OBSConfig
    voice_activity_detection: VADConfig
    auto_speech_recognition: ASRConfig
    minecraft: MinecraftConfig
    zerolan_live_robot_config: ZerolanLiveRobotConfig


def load_global_config():
    config_yaml: dict = utils.util.read_yaml('./config/config.yaml')

    live_stream_config = LiveStreamConfig(
        enable=config_yaml['live_stream']['enable'],
        platforms=config_yaml['live_stream']['platforms']
    )

    screenshot_config = ScreenshotConfig(
        enable=config_yaml['screenshot']['enable'],
        window_title=config_yaml['screenshot']['window_title'],
        k=config_yaml['screenshot']['k'],
        save_directory=config_yaml['screenshot']['save_directory']
    )

    image_captioning_config = ImageCaptioningConfig(
        enable=config_yaml['image_captioning']['enable'],
        debug=config_yaml['image_captioning']['debug'],
        host=config_yaml['image_captioning']['host'],
        port=config_yaml['image_captioning']['port'],
        models=config_yaml['image_captioning']['models']
    )

    text_to_speech_config = TextToSpeechConfig(
        enable=config_yaml['text_to_speech']['enable'],
        debug=config_yaml['text_to_speech']['debug'],
        host=config_yaml['text_to_speech']['host'],
        port=config_yaml['text_to_speech']['port'],
        save_directory=config_yaml['text_to_speech']['save_directory'],
        models=config_yaml['text_to_speech']['models']
    )

    large_language_model_config = LargeLanguageModelConfig(
        enable=config_yaml['large_language_model']['enable'],
        debug=config_yaml['large_language_model']['debug'],
        host=config_yaml['large_language_model']['host'],
        port=config_yaml['large_language_model']['port'],
        models=config_yaml['large_language_model']['models']
    )

    tone_analysis_config = ToneAnalysisConfig(
        enable=config_yaml['tone_analysis']['enable'],
        tone_analysis_template_path=config_yaml['tone_analysis']['tone_analysis_template_path']
    )

    obs_config = OBSConfig(
        enable=config_yaml['obs']['enable'],
        danmaku_output_path=config_yaml['obs']['danmaku_output_path'],
        tone_output_path=config_yaml['obs']['tone_output_path'],
        llm_output_path=config_yaml['obs']['llm_output_path']
    )

    vad_config = VADConfig(
        enable=config_yaml['voice_activity_detection']['enable'],
        save_dir=config_yaml['voice_activity_detection']['save_dir'],
        chunk=config_yaml['voice_activity_detection']['chunk'],
        sample_rate=config_yaml['voice_activity_detection']['sample_rate'],
        threshold=config_yaml['voice_activity_detection']['threshold'],
        max_mute_count=config_yaml['voice_activity_detection']['max_mute_count']
    )

    asr_config = ASRConfig(
        enable=config_yaml['auto_speech_recognition']['enable'],
        debug=config_yaml['auto_speech_recognition']['debug'],
        host=config_yaml['auto_speech_recognition']['host'],
        port=config_yaml['auto_speech_recognition']['port'],
        models=config_yaml['auto_speech_recognition']['models']
    )

    minecraft_config = MinecraftConfig(
        enable=config_yaml['minecraft']['enable']
    )

    zerolan_live_robot_config = ZerolanLiveRobotConfig(
        enable=config_yaml['zerolan_live_robot_config']['enable'],
        debug=config_yaml['zerolan_live_robot_config']['debug'],
        host=config_yaml['zerolan_live_robot_config']['host'],
        port=config_yaml['zerolan_live_robot_config']['port'],
        role_play_template_path=config_yaml['zerolan_live_robot_config']['role_play_template_path']
    )

    global_config = GlobalConfig(
        live_stream=live_stream_config,
        screenshot=screenshot_config,
        image_captioning=image_captioning_config,
        text_to_speech=text_to_speech_config,
        large_language_model=large_language_model_config,
        tone_analysis=tone_analysis_config,
        obs=obs_config,
        voice_activity_detection=vad_config,
        auto_speech_recognition=asr_config,
        minecraft=minecraft_config,
        zerolan_live_robot_config=zerolan_live_robot_config
    )

    return global_config


GLOBAL_CONFIG = load_global_config()
