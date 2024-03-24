import os
from os import PathLike

import yaml
from loguru import logger

from utils.util import is_valid_port


def read_yaml(path: str | PathLike):
    with open(file=path, mode='r', encoding='utf-8') as file:
        return yaml.safe_load(file)


def load_global_config(default_global_config_path: str | PathLike):
    """
    加载全局配置
    :param default_global_config_path:
    :return:
    """
    assert os.path.exists(
        default_global_config_path), \
        f'❌️ 全局配置文件不存在：路径 {default_global_config_path} 不存在。您可能需要将 config/template_config.yaml 更名为 config/global_config.yaml'
    global_config = read_yaml(path=default_global_config_path)
    logger.info('⚙️ 全局配置加载完毕')
    return global_config


def load_bilibili_live_config(global_config: dict):
    """
    加载 Bilibili 直播配置
    :return: tuple 包含 sessdata, bili_jct, buvid3, room_id（直播间 ID）四个配置项
    :raises AssertionError: 如果配置项缺失或格式有误
    """
    bilibili_live_config = global_config.get('bilibili_live_config', None)
    if not bilibili_live_config:
        raise ValueError(f'❌️ Bilibili 直播配置未填写或格式有误')
    sessdata = bilibili_live_config.get('sessdata', None)
    assert sessdata, f'❌️ bilibili_live_config 中的字段 sessdata 未填写或格式有误'
    bili_jct = bilibili_live_config.get('bili_jct', None)
    assert bili_jct, f'❌️ bilibili_live_config 中的字段 bili_jct 未填写或格式有误'
    buvid3 = bilibili_live_config.get('buvid3', None)
    assert buvid3, f'❌️ bilibili_live_config 中的字段 buvid3 未填写或格式有误'
    room_id = bilibili_live_config.get('room_id', 'room_id')
    assert room_id >= 0, f'❌️ bilibili_live_config 中的字段 room_id 应当是一个非负 int 型整数'
    logger.info('⚙️ Bilibili 直播配置加载完毕')
    return sessdata, bili_jct, buvid3, room_id


def load_screenshot_config(global_config: dict):
    """

    :param global_config:
    :return:
    """
    screenshot_config = global_config.get('screenshot_config', None)
    assert screenshot_config, f'❌️ 截屏配置未填写或格式有误'
    win_title = screenshot_config.get('win_title', None)
    assert win_title, f'❌️ 截屏配置中的字段 win_title 未填写或格式有误'
    k = screenshot_config.get('k', 0.9)
    assert 0 < k < 1, f'❌️ 截屏配置中的字段 win_title 必须在 0 ~ 1 之间'
    save_dir = screenshot_config.get('save_dir', '.tmp/screenshots')
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
        logger.warning(f'⚠️ 截屏配置中的字段 save_dir 所指向的目录不存在，已自动创建')
    assert os.path.isdir(save_dir), f'❌️ 截屏配置中的字段 save_dir 所指向的路径不是一个目录'
    logger.info('⚙️ 截屏配置加载完毕')
    return win_title, k, save_dir


def load_blip_image_captioning_large_config(global_config: dict):
    """
    加载模型 blip-image-captioning-large 的配置
    :param global_config:
    :return:
    """
    config = global_config.get('blip_image_captioning_large_config', None)
    assert config, f'❌️ 模型 blip-image-captioning-large 配置未填写或格式有误'
    model_path = config.get('model_path')
    if not os.path.exists(model_path):
        model_path = 'Salesforce/blip-image-captioning-large'
    text_prompt = config.get('text_prompt', 'There')
    logger.info('⚙️ 模型 blip-image-captioning-large 配置加载完毕')
    return model_path, text_prompt


def load_gpt_sovits_config(global_config: dict):
    gpt_sovits_config = global_config.get('gpt_sovits_service_config', None)
    assert gpt_sovits_config, f'❌️ GPT-SoVITS 服务配置未填写或格式有误'
    debug = gpt_sovits_config.get('debug', False)
    host = gpt_sovits_config.get('host', '127.0.0.1')
    port = gpt_sovits_config.get('port', 9880)
    save_dir = gpt_sovits_config.get('save_dir', '.tmp/wav_output')
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
        logger.warning('⚠️ GPT-SoVITS 服务配置中的字段 save_dir 所指向的目录不存在，已自动创建')

    logger.info('⚙️ GPT-SoVITS 服务配置加载完毕')
    return debug, host, port, save_dir


def load_tone_analysis_service_config(global_config: dict):
    tone_analysis_service_config = global_config.get('tone_analysis_service_config', None)
    assert tone_analysis_service_config, f'❌️ 语气分析服务配置未填写或格式有误'
    tone_template_path = tone_analysis_service_config.get('tone_template_path', 'template/tone_list.yaml')
    assert os.path.exists(tone_template_path), f'❌️ 语气分析服务配置中的字段 tone_template_path 所指向的路径不存在'
    prompt_for_llm_path = tone_analysis_service_config.get('prompt_for_llm_path', 'template/tone_prompt_4_llm.json')
    assert os.path.exists(prompt_for_llm_path), f'❌️ 语气分析服务配置中的字段 prompt_for_llm_path 所指向的路径不存在'

    logger.info('⚙️ 语气分析服务服务配置加载完毕')
    return tone_template_path, prompt_for_llm_path


def load_chatglm3_service_config(global_config: dict):
    config: dict = global_config.get('chatglm3_service_config', None)
    assert config, f'❌️ ChatGLM3 服务配置未填写或格式有误'
    debug = config.get('debug', False)
    host = config.get('host', '127.0.0.1')
    port = config.get('port', 8085)
    assert is_valid_port(port), f'❌️ ChatGLM3 服务配置中的字段 port 所代表的端口号不合法'
    tokenizer_path = config.get('tokenizer_path', "THUDM/chatglm3-6b")
    assert os.path.exists(tokenizer_path), f'❌️ ChatGLM3 服务配置中的字段 tokenizer_path 所指向的路径不存在'
    model_path = config.get('model_path', "THUDM/chatglm3-6b")
    assert os.path.exists(model_path), f'❌️ ChatGLM3 服务配置中的字段 model_path 所指向的路径不存在'
    quantize = config.get('quantize', 4)

    logger.info('⚙️ ChatGLM3 服务配置加载完毕')
    return debug, host, port, tokenizer_path, model_path, quantize


def load_obs_config(global_config: dict):
    config = global_config.get('obs_config')
    danmaku_output_path = config.get('danmaku_output_path', '.tmp/danmaku_output/output.txt')
    assert os.path.exists(danmaku_output_path), f'❌️ OBS 服务配置中的字段 danmaku_output_path 所指向的路径不存在'
    tone_output_path = config.get('tone_output_path', '.tmp/tone_output/output.txt')
    assert os.path.exists(tone_output_path), f'❌️ OBS 服务配置中的字段 tone_output_path 所指向的路径不存在'
    llm_output_path = config.get('llm_output_path', '.tmp/llm_output/output.txt')
    assert os.path.exists(llm_output_path), f'❌️ OBS 服务配置中的字段 llm_output_path 所指向的路径不存在'
    return danmaku_output_path, tone_output_path, llm_output_path


def load_zerolan_live_robot_config(global_config: dict):
    config = global_config.get('zerolan_live_robot_config', None)
    assert config, f'❌️ Zerolan Live Robot 服务配置未填写或格式有误'
    custom_prompt_path = config.get('custom_prompt_path', 'template/custom_prompt2.json')
    assert os.path.exists(
        custom_prompt_path), f'❌️ Zerolan Live Robot 服务配置中的字段 custom_prompt_path 所指向的路径不存在'
    debug = config.get('debug', False)
    host = config.get('host', '127.0.0.1')
    port = config.get('port', 11451)
    logger.info('⚙️ Zerolan Live Robot 服务服务配置加载完毕')
    return debug, host, port, custom_prompt_path
