from dataclasses import dataclass
from os import PathLike


# Bilibili 直播配置
@dataclass
class BilibiliLiveConfig:
    # 获取方式[详见](https://nemo2011.github.io/bilibili-api/#/get-credential)
    sessdata: str
    bili_jct: str
    buvid3: str
    # 直播间 ID （应为数字）
    room_id: int
    # 是否启动本服务
    enabled: bool = True


# 截屏配置
@dataclass
class ScreenshotConfig:
    # 窗口标题（会自动查找符合该标题的第一个窗口）
    win_title: str
    # 缩放因子（为了防止屏幕被截取窗口）
    k: float = 0.9
    # 截取的图片存放位置
    save_dir: str | PathLike = R'.tmp/screenshots'


# blip-image-captioning-large 服务配置
@dataclass
class BlipImageCaptioningLargeConfig:
    model_path: str | PathLike
    text_prompt: str
    debug: bool = False
    host: str = '127.0.0.1'
    port: int = 5926

    def url(self, protocol: str = 'http'):
        return f'{protocol}://{self.host}:{self.port}'


# GPT-SoVITS 服务配置
@dataclass
class GPTSoVITSServiceConfig:
    # 是否以调试模式运行
    debug: bool = False
    # GPT-SoVITS 服务地址
    host: str = '127.0.0.1'
    # GPT-SoVITS 服务端口
    port: int = 9880
    # 音频临时文件夹
    save_dir: str | PathLike = '.tmp/wav_output'

    def url(self, protocol: str = 'http'):
        return f'{protocol}://{self.host}:{self.port}'


# 语气分析服务配置
@dataclass
class ToneAnalysisServiceConfig:
    # 语气分析模板地址
    tone_analysis_template_path: str | PathLike = R'template/tone_analysis_template.yaml'


@dataclass
class LLMServiceConfig:
    # LLM 服务名（即用什么模型）
    llm_name: str = 'chatglm3'
    # LLM 服务地址
    host: str = '127.0.0.1'
    # LLM 服务端口
    port: int = 8085

    def url(self, protocol: str = 'http'):
        return f'{protocol}://{self.host}:{self.port}'


# OBS 服务配置
@dataclass
class OBSConfig:
    # 弹幕输出字幕文件
    danmaku_output_path: str | PathLike = R'.tmp/danmaku_output/output.txt'
    # 语气输出字幕文件
    tone_output_path: str | PathLike = R'.tmp/tone_output/output.txt'
    # 大语言模型输出字幕文件
    llm_output_path: str | PathLike = R'.tmp/llm_output/output.txt'


# VAD 检测配置
@dataclass
class VADConfig:
    # 用户语音保存位置
    save_dir: str | PathLike = R'.tmp/records'
    # 块大小
    chunk: int = 4096
    # 采样率
    sample_rate: int = 16000
    # 激活阈值
    threshold: int = 600
    # 最大容许静音数
    max_mute_count: int = 10


# 自动语音识别配置
@dataclass
class ASRConfig:
    # 语音识别模型路径
    speech_model_path: str | PathLike = R'paraformer-zh'
    # VAD 模型路径
    vad_model_path: str | PathLike = R'fsmn-vad'
    # 是否以调试模式运行
    debug: bool = False
    # 自动语音识别服务地址
    host: str = '127.0.0.1'
    # 自动语音识别服务端口
    port: int = 11005

    def url(self, protocol: str = 'http'):
        return f'{protocol}://{self.host}:{self.port}'


# 本项目配置
@dataclass
class ZerolanLiveRobotConfig:
    # 是否以调试模式运行
    debug: bool = False
    # ChatGLM3 服务地址
    host: str = '127.0.0.1'
    # ChatGLM3 服务端口
    port: int = 11451
    # 提示词模板
    custom_prompt_path: str | PathLike = R'template/custom_prompt.json'

    def url(self, protocol: str = 'http'):
        return f'{protocol}://{self.host}:{self.port}'
