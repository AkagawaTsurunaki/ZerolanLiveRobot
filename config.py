from dataclasses import dataclass
from typing import List, Optional


@dataclass
class BilibiliConfig:
    sessdata: Optional[str] = None
    bili_jct: Optional[str] = None
    buvid3: Optional[str] = None
    room_id: Optional[int] = None


@dataclass
class PlatformConfig:
    bilibili: Optional[BilibiliConfig] = None


@dataclass
class LiveStreamConfig:
    enable: bool = True
    platform: Optional[List[PlatformConfig]] = None


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
    models: Optional[List[dict]] = None


@dataclass
class TextToSpeechConfig:
    enable: bool = True
    debug: bool = False
    host: str = "127.0.0.1"
    port: int = 9880
    save_directory: str = ".tmp/wav_output"
    models: Optional[List[dict]] = None


@dataclass
class LargeLanguageModelConfig:
    enable: bool = True
    debug: bool = False
    host: str = "127.0.0.1"
    port: int = 9881
    models: Optional[List[dict]] = None


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
class GlobalConfig:
    live_stream: LiveStreamConfig = LiveStreamConfig()
    screenshot: ScreenshotConfig = ScreenshotConfig()
    image_captioning: ImageCaptioningConfig = ImageCaptioningConfig()
    text_to_speech: TextToSpeechConfig = TextToSpeechConfig()
    large_language_model: LargeLanguageModelConfig = LargeLanguageModelConfig()
    tone_analysis: ToneAnalysisConfig = ToneAnalysisConfig()
    obs: OBSConfig = OBSConfig()
    voice_activity_detection: VADConfig = VADConfig()
    auto_speech_recognition: ASRConfig = ASRConfig()
    zerolan_live_robot_config: ZerolanLiveRobotConfig = ZerolanLiveRobotConfig()
