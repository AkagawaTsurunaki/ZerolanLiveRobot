import os
from os import PathLike

from loguru import logger

import utils.util
from config.global_config import BilibiliLiveConfig, ScreenshotConfig, BlipImageCaptioningLargeConfig, \
    GPTSoVITSServiceConfig, ToneAnalysisServiceConfig, OBSConfig, ASRConfig, VADConfig, \
    ZerolanLiveRobotConfig, LLMServiceConfig
from utils.util import is_valid_port, create_file_if_not_exists, read_yaml


def _load_global_config(path: str | PathLike = 'config/global_config.yaml'):
    """
    加载全局配置
    :param path:
    :return:
    """
    assert os.path.exists(
        path), \
        f'❌️ 全局配置文件不存在：路径 {path} 不存在。您可能需要将 config/template_config.yaml 更名为 config/global_config.yaml'
    global_config = read_yaml(path=path)
    if not os.path.exists('.tmp'):
        os.mkdir('.tmp')
    logger.info('⚙️ 全局配置加载完毕')
    return global_config


GLOBAL_CONFIG = _load_global_config()


def load_bilibili_live_config():
    """
    加载 Bilibili 直播配置

    :return: tuple 包含 sessdata, bili_jct, buvid3, room_id（直播间 ID）四个配置项
    :raises AssertionError: 如果配置项缺失或格式有误
    """
    config: dict = GLOBAL_CONFIG.get('bilibili_live_config', None)
    assert config, f'❌️ Bilibili 直播配置未填写或格式有误'

    sessdata = config.get('sessdata', None)
    assert sessdata, f'❌️ bilibili_live_config 中的字段 sessdata 未填写或格式有误'

    bili_jct = config.get('bili_jct', None)
    assert bili_jct, f'❌️ bilibili_live_config 中的字段 bili_jct 未填写或格式有误'

    buvid3 = config.get('buvid3', None)
    assert buvid3, f'❌️ bilibili_live_config 中的字段 buvid3 未填写或格式有误'

    room_id = config.get('room_id', 'room_id')
    assert room_id and room_id >= 0, f'❌️ bilibili_live_config 中的字段 room_id 应当是一个非负 int 型整数'

    return BilibiliLiveConfig(
        enabled=True,
        sessdata=sessdata,
        bili_jct=bili_jct,
        buvid3=buvid3,
        room_id=room_id
    )


def load_screenshot_config():
    """
    加载截图配置

    :return: tuple, 包含截图窗口标题(win_title)、匹配度阈值(k)和保存目录(save_dir)的元组
    :raises AssertionError: 当截图配置中关键信息未填写或格式有误时引发断言错误
    """
    config: dict = GLOBAL_CONFIG.get('screenshot_config', None)
    assert config, f'❌️ 截屏配置未填写或格式有误'

    win_title = config.get('win_title', None)
    assert win_title, f'❌️ 截屏配置中的字段 win_title 未填写或格式有误'

    k = config.get('k', 0.9)
    assert 0 < k < 1, f'❌️ 截屏配置中的字段 win_title 必须在 0 ~ 1 之间'

    save_dir = config.get('save_dir', '.tmp/screenshots')
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    assert os.path.isdir(save_dir), f'❌️ 截屏配置中的字段 save_dir 所指向的路径不是一个目录'

    return ScreenshotConfig(
        win_title=win_title,
        k=k,
        save_dir=save_dir
    )


def load_blip_image_captioning_large_config() -> BlipImageCaptioningLargeConfig:
    """
    加载模型 blip-image-captioning-large 的配置
    :return:
    """
    config: dict = GLOBAL_CONFIG.get('blip_image_captioning_large_config', None)
    assert config, f'❌️ 模型 blip-image-captioning-large 配置未填写或格式有误'

    model_path = config.get('model_path', 'Salesforce/blip-image-captioning-large')
    assert os.path.exists(model_path), f'❌️ blip-image-captioning-large 服务配置中的字段 model_path 所指向的路径不存在'

    debug = config.get('debug', False)
    host = config.get('host', '127.0.0.1')

    port = config.get('port', 5926)
    assert is_valid_port(port), f'❌️ blip-image-captioning-large 服务所配置的端口不合法'

    text_prompt = config.get('text_prompt', 'There')

    return BlipImageCaptioningLargeConfig(
        model_path=model_path,
        text_prompt=text_prompt,
        debug=debug,
        host=host,
        port=port
    )


def load_gpt_sovits_config():
    config: dict = GLOBAL_CONFIG.get('gpt_sovits_service_config', None)
    assert config, f'❌️ GPT-SoVITS 服务配置未填写或格式有误'

    debug = config.get('debug', False)

    host = config.get('host', '127.0.0.1')

    port = config.get('port', 9880)
    assert utils.util.is_valid_port(port), f'❌️ GPT-SoVITS 服务所配置的端口不合法'

    save_dir = config.get('save_dir', '.tmp/wav_output')
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    return GPTSoVITSServiceConfig(
        debug=debug,
        host=host,
        port=port,
        save_dir=save_dir
    )


def load_tone_analysis_service_config():
    config: dict = GLOBAL_CONFIG.get('tone_analysis_service_config', None)
    assert config, f'❌️ 语气分析服务配置未填写或格式有误'

    tone_template_path = config.get('tone_template_path', 'template/tone_analysis_template.yaml')
    assert os.path.exists(tone_template_path), f'❌️ 语气分析服务配置中的字段 tone_template_path 所指向的路径不存在'

    return ToneAnalysisServiceConfig(
        tone_analysis_template_path=tone_template_path
    )


def load_llm_service_config():
    config: dict = GLOBAL_CONFIG['llm_service_config']
    llm_name = config['llm_name']
    host = config['host']
    port = config['port']
    return LLMServiceConfig(
        llm_name=llm_name,
        host=host,
        port=port
    )


def load_obs_config():
    config: dict = GLOBAL_CONFIG.get('obs_config')

    danmaku_output_path = config.get('danmaku_output_path', '.tmp/danmaku_output/output.txt')
    create_file_if_not_exists(danmaku_output_path)
    assert os.path.exists(danmaku_output_path), f'❌️ OBS 服务配置中的字段 danmaku_output_path 所指向的路径不存在'

    tone_output_path = config.get('tone_output_path', '.tmp/tone_output/output.txt')
    create_file_if_not_exists(tone_output_path)
    assert os.path.exists(tone_output_path), f'❌️ OBS 服务配置中的字段 tone_output_path 所指向的路径不存在'

    llm_output_path = config.get('llm_output_path', '.tmp/llm_output/output.txt')
    create_file_if_not_exists(llm_output_path)
    assert os.path.exists(llm_output_path), f'❌️ OBS 服务配置中的字段 llm_output_path 所指向的路径不存在'

    return OBSConfig(
        danmaku_output_path=danmaku_output_path,
        tone_output_path=tone_output_path,
        llm_output_path=llm_output_path
    )


def load_asr_config():
    config = GLOBAL_CONFIG.get('asr_config')

    speech_model_path = config.get('speech_model_path', 'paraformer-zh')
    assert os.path.exists(speech_model_path), f'❌️ 自动语音识别服务配置中的字段 speech_model_path 所指向的路径不存在'

    vad_model_path = config.get('speech_model_path', 'fsmn-vad')
    assert os.path.exists(vad_model_path), f'❌️ 自动语音识别服务配置中的字段 vad_model_path 所指向的路径不存在'

    host = config.get('host', '127.0.0.1')

    port = config.get('port', 9882)
    assert utils.util.is_valid_port(port), f'❌️ 自动语音识别服务所配置的端口不合法'
    debug = config.get('debug', False)

    return ASRConfig(
        vad_model_path=vad_model_path,
        speech_model_path=speech_model_path,
        port=port,
        host=host,
        debug=debug
    )


def load_vad_config():
    config = GLOBAL_CONFIG.get('vad_config')

    save_dir = config.get('save_dir', '.tmp/records')
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    chunk = config.get('chunk', 4096)
    assert chunk > 0, f'❌️ VAD 服务配置中的字段 chunk 必须是正整数'

    sample_rate = config.get('sample_rate', 16000)
    assert sample_rate > 0, f'❌️ VAD 服务配置中的字段 sample_rate 必须是正整数'

    threshold = config.get('threshold', 600)
    assert threshold > 0, f'❌️ VAD 服务配置中的字段 threshold 必须是正整数'

    max_mute_count = config.get('max_mute_count', 10)
    assert max_mute_count > 0, f'❌️ VAD 服务配置中的字段 max_mute_count 必须是正整数'

    return VADConfig(
        save_dir=save_dir,
        chunk=chunk,
        sample_rate=sample_rate,
        threshold=threshold,
        max_mute_count=max_mute_count
    )


def load_zerolan_live_robot_config():
    config = GLOBAL_CONFIG.get('zerolan_live_robot_config', None)
    assert config, f'❌️ Zerolan Live Robot 服务配置未填写或格式有误'

    role_play_template_path = config.get('role_play_template_path', 'template/role_play_template.yaml')
    assert os.path.exists(
        role_play_template_path), f'❌️ Zerolan Live Robot 服务配置中的字段 custom_prompt_path 所指向的路径不存在'

    debug = config.get('debug', False)
    host = config.get('host', '127.0.0.1')

    port = config.get('port', 11451)
    assert is_valid_port(port), f'❌️ Zerolan Live Robot 服务配置中的字段 port 所代表的端口号不合法'

    return ZerolanLiveRobotConfig(
        debug=debug,
        host=host,
        port=port,
        role_play_template_path=role_play_template_path
    )
