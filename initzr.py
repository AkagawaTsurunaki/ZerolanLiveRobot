import os
from os import PathLike

from loguru import logger

import utils.util
from config.global_config import BilibiliLiveConfig, ScreenshotConfig, BlipImageCaptioningLargeConfig, \
    GPTSoVITSServiceConfig, ToneAnalysisServiceConfig, OBSConfig, ASRConfig, VADConfig, \
    ZerolanLiveRobotConfig, LLMServiceConfig
from utils.util import is_valid_port, create_file_if_not_exists, read_yaml
from utils.datacls import ServiceNameConst as SNR


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


def load_blip_image_captioning_large_config() -> BlipImageCaptioningLargeConfig:
    """
    Load the config of the Image-to-Caption service.
    :return:
    """
    config: dict = GLOBAL_CONFIG.get('blip_image_captioning_large_config', None)
    assert config, f'❌️ Failed to load the config of the Image-to-Caption service because the config object is None.'

    model_path = config.get('model_path', SNR.BLIP)
    assert os.path.exists(model_path), f'❌️ blip-image-captioning-large 服务配置中的字段 model_path 所指向的路径不存在'

    debug = config.get('debug', False)
    host = config.get('host', '127.0.0.1')

    port = config.get('port', 5926)
    assert is_valid_port(port), f'❌️ {SNR.BLIP} 服务所配置的端口不合法'

    text_prompt = config.get('text_prompt', 'There')

    return BlipImageCaptioningLargeConfig(
        model_path=model_path,
        text_prompt=text_prompt,
        debug=debug,
        host=host,
        port=port
    )


def load_tone_analysis_service_config():
    config: dict = GLOBAL_CONFIG.get('tone_analysis_service_config', None)
    assert config, f'❌️ 语气分析服务配置未填写或格式有误'

    tone_template_path = config.get('tone_analysis_template_path', 'template/tone_analysis_template.yaml')
    assert os.path.exists(tone_template_path), f'❌️ 语气分析服务配置中的字段 tone_template_path 所指向的路径不存在'

    return ToneAnalysisServiceConfig(
        tone_analysis_template_path=tone_template_path
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
