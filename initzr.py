import os
from os import PathLike

from loguru import logger

from config.global_config import ToneAnalysisServiceConfig, OBSConfig, ZerolanLiveRobotConfig
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
