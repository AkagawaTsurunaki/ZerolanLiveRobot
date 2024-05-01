import os.path
from dataclasses import dataclass
from typing import List

import common.util
from common import util
from common.datacls import PlatformConst
from common.util import is_valid_port
from common.datacls import ServiceNameConst as SNC


@dataclass
class PlatformConfig:
    platform_name: str


@dataclass
class BilibiliConfig(PlatformConfig):
    room_id: int
    sessdata: str
    bili_jct: str
    buvid3: str


@dataclass
class LiveStreamConfig:
    enable: bool = True
    platforms: List[PlatformConfig | BilibiliConfig] = None


@dataclass
class ScreenshotConfig:
    enable: bool = True
    window_title: str = "Minecraft"
    k: float = 0.9
    save_directory: str = ".tmp/screenshots"


@dataclass
class ImageCaptioningModelConfig:
    model_name: str


@dataclass
class BlipConfig(ImageCaptioningModelConfig):
    text_prompt: str
    model_path: str


@dataclass
class ImageCaptioningConfig:
    enable: bool = True
    debug: bool = False
    host: str = "127.0.0.1"
    port: int = 9879
    models: List[ImageCaptioningModelConfig | BlipConfig] = None


@dataclass
class TTSModelConfig:
    model_name: str


@dataclass
class GPTSoVITSConfig(TTSModelConfig):
    ...


@dataclass
class TextToSpeechConfig:
    enable: bool = True
    debug: bool = False
    host: str = "127.0.0.1"
    port: int = 9880
    save_directory: str = ".tmp/wav_output"
    models: List[TTSModelConfig | GPTSoVITSConfig] = None


@dataclass
class LLMConfig:
    model_name: str


@dataclass
class ChatGlm3Config(LLMConfig):
    model_path: str
    quantize: int


@dataclass
class QwenConfig(LLMConfig):
    model_path: str
    quantize: int
    loading_mode: str


@dataclass
class YiConfig(LLMConfig):
    model_path: str
    loading_mode: str


@dataclass
class ShisaConfig(LLMConfig):
    model_path: str
    loading_mode: str


@dataclass
class LLMServiceConfig:
    enable: bool = True
    debug: bool = False
    host: str = "127.0.0.1"
    port: int = 9881
    models: List[LLMConfig | ChatGlm3Config | QwenConfig | YiConfig | ShisaConfig] = None


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
class ASRModelConfig:
    model_name: str


@dataclass
class SpeechParaformerConfig(ASRModelConfig):
    model_path: str
    version: str


@dataclass
class ASRConfig:
    enable: bool = True
    debug: bool = False
    host: str = "127.0.0.1"
    port: int = 9882
    models: List[ASRModelConfig | SpeechParaformerConfig] = None


@dataclass
class ZerolanLiveRobotConfig:
    enable: bool = True
    debug: bool = False
    host: str = "127.0.0.1"
    port: int = 9888
    role_play_template_path: str = "template/role_play_template_short.yaml"
    lang: str = 'zh'


@dataclass
class MinecraftConfig:
    enable: bool = True
    host: str = '127.0.0.1'
    port: int = 12546
    debug: bool = False


@dataclass
class GlobalConfig:
    live_stream: LiveStreamConfig
    screenshot: ScreenshotConfig
    image_captioning: ImageCaptioningConfig
    text_to_speech: TextToSpeechConfig
    large_language_model: LLMServiceConfig
    tone_analysis: ToneAnalysisConfig
    obs: OBSConfig
    voice_activity_detection: VADConfig
    auto_speech_recognition: ASRConfig
    minecraft: MinecraftConfig
    zerolan_live_robot_config: ZerolanLiveRobotConfig


def _safe_get_model_path(model: dict, model_name: str, cfg_item: str) -> str:
    model_path = model.get('model_path', model_name)
    if model_path != model_name:
        assert os.path.exists(model_path), \
            f'Invalid configuration item "{cfg_item}": Path "{model_path}" does not exist.'
    return model_path


def _safe_get_cur_model(cfg: dict, cfg_item_name: str) -> (str, dict):
    models = cfg.get('models')
    assert len(models) == 1, \
        f'Invalid configuration item "{cfg_item_name}.models": 1 model excepted, but now {len(models)}.'
    model = models[0]
    model_name = next(iter(model))
    return model_name, model.get(model_name, None)


def _safe_get_model_quantize(model: dict, model_name: str) -> int:
    quantize = model.get('quantize', None)
    assert quantize and quantize in [4, 8], \
        f'Invalid configuration item "large_language_model.models.{model_name}.quantize": 4 or 8 expected, but now {quantize}'
    return quantize


def _safe_get_app_args(cfg: dict, cfg_item_name: str) -> (str, int, bool):
    debug = cfg.get('debug', False)
    host = cfg.get('host', None)
    assert host, f'Invalid configuration item "{cfg_item_name}.host": None got.'
    port = cfg.get('port', None)
    assert port and is_valid_port(port), \
        f'Invalid configuration item "{cfg_item_name}.port": {port} is not a valid port.'
    return host, port, debug


def _safe_get_path(path: str, cfg_item_name: str) -> str:
    assert os.path.exists(path), \
        f'Invalid configuration item "{cfg_item_name}": "{path}" does not exist.'
    return path


def load_live_stream_config(cfg: dict) -> LiveStreamConfig:
    enable: bool = cfg.get('enable', None)
    assert enable is not None, \
        f'Invalid configuration item "live_stream.enable": True or False excepted, but now {enable}.'
    if enable:
        platforms = cfg.get('platforms')
        assert len(platforms) == 1, \
            f'Invalid configuration item "live_stream.platforms": 1 platform excepted, but now {len(platforms)}.'
        platform = platforms[0]
        platform_name = next(iter(platform))

        if PlatformConst.BILIBILI == platform_name:
            # Bilibili
            sessdata = platform[PlatformConst.BILIBILI]['sessdata']
            bili_jct = platform[PlatformConst.BILIBILI]['bili_jct']
            buvid3 = platform[PlatformConst.BILIBILI]['buvid3']
            room_id = platform[PlatformConst.BILIBILI]['room_id']
            bili_cfg = BilibiliConfig(room_id=room_id,
                                      sessdata=sessdata,
                                      buvid3=buvid3,
                                      bili_jct=bili_jct,
                                      platform_name=PlatformConst.BILIBILI)
            return LiveStreamConfig(enable=enable, platforms=[bili_cfg])
        else:
            raise NotImplementedError(f'Live streaming platform {platform_name} is not supported.')
    else:
        return LiveStreamConfig(enable=enable)


def load_screenshot_config(cfg: dict) -> ScreenshotConfig:
    enable: bool = cfg.get('enable', None)
    assert enable is not None, \
        f'Invalid configuration item "screenshot.enable": True or False excepted, but now {enable}.'
    if enable:
        window_title = cfg.get('window_title', None)
        assert window_title and len(window_title) != 0, \
            f'Invalid configuration item "screenshot.window_title": Should has at least 1 character.'
        k = cfg.get('k', None)
        assert k and 0.0 < k < 1.0, f'Invalid configuration item "screenshot.k": Should greater than 0 but less than 1.'
        save_directory = _safe_get_path(cfg['save_directory'], 'screenshot.save_directory')
        return ScreenshotConfig(enable=enable, window_title=window_title, k=k, save_directory=save_directory)
    else:
        return ScreenshotConfig(enable=enable)


def load_image_captioning_config(cfg: dict) -> ImageCaptioningConfig:
    enable: bool = cfg.get('enable', None)
    assert enable is not None, \
        f'Invalid configuration item "image_captioning.enable": True or False excepted, but now {enable}.'
    if enable:
        host, port, debug = _safe_get_app_args(cfg, "image_captioning")
        model_name, model = _safe_get_cur_model(cfg, 'image_captioning')

        if SNC.BLIP == model_name:
            model_path = _safe_get_model_path(model, model_name=SNC.BLIP,
                                              cfg_item="image_captioning.models.Salesforce/blip-image-captioning-large.model_path")
            text_prompt = cfg.get('text_prompt', None)
            assert util.is_english_string(
                text_prompt), f'Invalid configuration item "image_captioning.models.Salesforce/blip-image-captioning-large.text_prompt": English only.'
            blip_config = BlipConfig(model_name=SNC.BLIP, model_path=model_path, text_prompt=text_prompt)

            return ImageCaptioningConfig(enable=enable, debug=debug, host=host, port=port, models=[blip_config])
        else:
            raise NotImplementedError(f'Model {model_name} is not supported.')

    else:
        return ImageCaptioningConfig(enable=enable)


def load_tts_config(cfg: dict) -> TextToSpeechConfig:
    enable: bool = cfg.get('enable', None)
    assert enable is not None, \
        f'Invalid configuration item "image_captioning.enable": True or False excepted, but now {enable}.'
    if enable:
        host, port, debug = _safe_get_app_args(cfg, "text_to_speech")

        save_directory = cfg.get('save_directory', None)
        assert os.path.exists(save_directory), \
            f'Invalid configuration item "text_to_speech.save_directory": "{save_directory}" does not exist.'

        models = cfg.get('models')
        assert len(models) == 1, \
            f'Invalid configuration item "text_to_speech.models": 1 model excepted, but now {len(models)}.'
        model = models[0]
        model_name = next(iter(model))

        if SNC.GPT_SOVITS == model_name:
            assert util.is_url_online(f'http://{host}:{port}'), \
                f'TTS service failure: GPT-SoVITS service is not online.'
            gpt_sovits_config = GPTSoVITSConfig(model_name=SNC.GPT_SOVITS)
            return TextToSpeechConfig(enable=enable, debug=debug, host=host, port=port, save_directory=save_directory,
                                      models=[gpt_sovits_config])
        else:
            raise NotImplementedError(f'Model {model_name} is not supported.')

    else:
        return TextToSpeechConfig(enable=enable)


def load_llm_config(cfg: dict) -> LLMServiceConfig:
    enable: bool = cfg.get('enable', None)
    assert enable is not None, \
        f'Invalid configuration item "large_language_model.enable": True or False excepted, but now {enable}.'
    if enable:
        host, port, debug = _safe_get_app_args(cfg, 'large_language_model')
        model_name, model = _safe_get_cur_model(cfg, 'large_language_model')

        if SNC.CHATGLM3 == model_name:
            model_path = _safe_get_model_path(model, model_name=SNC.CHATGLM3,
                                              cfg_item=f'large_language_model.models.{SNC.CHATGLM3}')
            quantize = _safe_get_model_quantize(model, model_name=SNC.CHATGLM3)
            chatglm_config = ChatGlm3Config(model_name=SNC.CHATGLM3, model_path=model_path, quantize=quantize)
            return LLMServiceConfig(enable=enable, debug=debug, host=host, port=port, models=[chatglm_config])

        elif SNC.QWEN == model_name:
            model_path = _safe_get_model_path(model, model_name=SNC.QWEN,
                                              cfg_item=f'large_language_model.models.{SNC.QWEN}')
            quantize = _safe_get_model_quantize(model, model_name=SNC.QWEN)
            loading_mode = model.get('loading_mode', 'auto')
            qwen_config = QwenConfig(model_name=SNC.QWEN, model_path=model_path, loading_mode=loading_mode,
                                     quantize=quantize)
            return LLMServiceConfig(enable=enable, debug=debug, host=host, port=port, models=[qwen_config])

        elif SNC.YI == model_name:
            model_path = _safe_get_model_path(model, model_name=SNC.YI,
                                              cfg_item=f'large_language_model.models.{SNC.YI}')
            loading_mode = model.get('loading_mode', 'auto')
            yi_config = YiConfig(model_name=SNC.YI, model_path=model_path, loading_mode=loading_mode)

            return LLMServiceConfig(enable=enable, debug=debug, host=host, port=port, models=[yi_config])
        elif SNC.SHISA == model_name:
            model_path = _safe_get_model_path(model, model_name=SNC.SHISA,
                                              cfg_item=f'large_language_model.models.{SNC.SHISA}')
            loading_mode = model.get('loading_mode', 'auto')
            shisa_config = ShisaConfig(model_name=SNC.SHISA, model_path=model_path, loading_mode=loading_mode)

            return LLMServiceConfig(enable=enable, debug=debug, host=host, port=port, models=[shisa_config])
        else:
            raise NotImplementedError(f'Model {model_name} is not supported.')
    else:
        return LLMServiceConfig(enable=enable)


def load_tone_ana(cfg: dict) -> ToneAnalysisConfig:
    enable: bool = cfg.get('enable', None)
    assert enable is not None, \
        f'Invalid configuration item "tone_analysis.enable": True or False excepted, but now {enable}.'
    if enable:
        tone_analysis_template_path = _safe_get_path(cfg.get('tone_analysis_template_path', None),
                                                     'tone_analysis.tone_analysis_template_path')
        return ToneAnalysisConfig(enable=enable, tone_analysis_template_path=tone_analysis_template_path)
    else:
        return ToneAnalysisConfig(enable=enable)


def load_obs_config(cfg: dict) -> OBSConfig:
    enable: bool = cfg.get('enable', None)
    assert enable is not None, \
        f'Invalid configuration item "obs.enable": True or False excepted, but now {enable}.'
    if enable:
        danmaku_output_path = _safe_get_path(cfg.get('danmaku_output_path', None), 'obs.danmaku_output_path')
        tone_output_path = _safe_get_path(cfg.get('tone_output_path', None), 'obs.tone_output_path')
        llm_output_path = _safe_get_path(cfg.get('llm_output_path', None), 'obs.llm_output_path')
        return OBSConfig(enable=enable, danmaku_output_path=danmaku_output_path, tone_output_path=tone_output_path,
                         llm_output_path=llm_output_path)
    else:
        return OBSConfig(enable=enable)


def load_vad_config(cfg: dict) -> VADConfig:
    enable: bool = cfg.get('enable', None)
    assert enable is not None, \
        f'Invalid configuration item "voice_activity_detection.enable": True or False excepted, but now {enable}.'
    if enable:
        save_dir = _safe_get_path(cfg.get('save_directory'), 'voice_activity_detection.save_directory')

        chunk = cfg.get('chunk', 4096)
        assert chunk > 0, f'Invalid configuration item "voice_activity_detection.chunk": Must greater than 0.'

        sample_rate = cfg.get('sample_rate', 16000)
        assert sample_rate > 0, f'Invalid configuration item "voice_activity_detection.sample_rate": Must greater than 0.'

        threshold = cfg.get('threshold', 600)
        assert threshold > 0, f'Invalid configuration item "voice_activity_detection.threshold": Must greater than 0.'

        max_mute_count = cfg.get('max_mute_count', 10)
        assert max_mute_count > 0, f'Invalid configuration item "voice_activity_detection.max_mute_count": Must greater than 0.'

        return VADConfig(save_dir=save_dir, enable=enable, threshold=threshold, sample_rate=sample_rate,
                         max_mute_count=max_mute_count, chunk=chunk)
    else:
        return VADConfig(enable=enable)


def load_asr_config(cfg: dict) -> ASRConfig:
    enable: bool = cfg.get('enable', None)
    assert enable is not None, \
        f'Invalid configuration item "auto_speech_recognition.enable": True or False excepted, but now {enable}.'
    if enable:
        host, port, debug = _safe_get_app_args(cfg, 'auto_speech_recognition')
        model_name, model = _safe_get_cur_model(cfg, 'auto_speech_recognition')
        if SNC.PARAFORMER == model_name:
            model_path = _safe_get_model_path(model, model_name=SNC.PARAFORMER,
                                              cfg_item=f'auto_speech_recognition.models.{SNC.PARAFORMER}')
            version = model.get('version', None)
            assert version, \
                f'Invalid configuration item "auto_speech_recognition.models.speech_paraformer.version": No version.'

            sp_cfg = SpeechParaformerConfig(model_path=model_path, version=version, model_name=SNC.PARAFORMER)

            return ASRConfig(enable=enable, host=host, port=port, debug=debug, models=[sp_cfg])
        else:
            raise NotImplementedError(f'Model {model_name} is not supported.')
    else:
        return ASRConfig(enable=enable)


def load_minecraft_config(cfg: dict) -> MinecraftConfig:
    enable: bool = cfg.get('enable', None)
    assert enable is not None, \
        f'Invalid configuration item "minecraft.enable": True or False excepted, but now {enable}.'
    if enable:
        host, port, debug = _safe_get_app_args(cfg, 'minecraft')
        return MinecraftConfig(enable=enable, host=host, debug=debug, port=port)
    else:
        return MinecraftConfig(enable=enable)


def load_zrl_config(cfg: dict) -> ZerolanLiveRobotConfig:
    enable: bool = cfg.get('enable', None)
    assert enable is not None, \
        f'Invalid configuration item "zerolan_live_robot_config.enable": True or False excepted, but now {enable}.'

    if enable:
        lang = cfg.get('lang')
        assert lang in ['zh', 'en', 'ja']
        host, port, debug = _safe_get_app_args(cfg, 'zerolan_live_robot_config')
        role_play_template_path = _safe_get_path(cfg['role_play_template_path'],
                                                 'zerolan_live_robot_config.role_play_template_path')
        return ZerolanLiveRobotConfig(enable=enable, host=host, port=port, debug=debug,
                                      role_play_template_path=role_play_template_path, lang=lang)
    else:
        return ZerolanLiveRobotConfig(enable=enable)


def load_global_config():
    config_yaml: dict = common.util.read_yaml('./config/config.yaml')

    global_config = GlobalConfig(
        live_stream=load_live_stream_config(config_yaml['live_stream']),
        screenshot=load_screenshot_config(config_yaml['screenshot']),
        image_captioning=load_image_captioning_config(config_yaml['image_captioning']),
        text_to_speech=load_tts_config(config_yaml['text_to_speech']),
        large_language_model=load_llm_config(config_yaml['large_language_model']),
        tone_analysis=load_tone_ana(config_yaml['tone_analysis']),
        obs=load_obs_config(config_yaml['obs']),
        voice_activity_detection=load_vad_config(config_yaml['voice_activity_detection']),
        auto_speech_recognition=load_asr_config(config_yaml['auto_speech_recognition']),
        minecraft=load_minecraft_config(config_yaml['minecraft']),
        zerolan_live_robot_config=load_zrl_config(config_yaml['zerolan_live_robot_config'])
    )

    return global_config


GLOBAL_CONFIG = load_global_config()
