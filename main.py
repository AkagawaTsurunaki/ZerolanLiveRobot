import asyncio
import sys
import threading

from loguru import logger

import asr.service
import audio_player.service
import controller.service
import minecraft.py.service
import vad.service
from bilibili import service as bili_serv
from blip_img_cap import service as blip_serv
from gptsovits import service as gptsovits_serv
from initzr import load_global_config, load_bilibili_live_config, load_blip_image_captioning_large_config, \
    load_screenshot_config, load_gpt_sovits_config, load_tone_analysis_service_config, load_chatglm3_service_config, \
    load_zerolan_live_robot_config, load_obs_config, load_asr_config, load_vad_config
from lifecircle import service_start
from obs import service as obs_serv
from scrnshot import service as scrn_serv
from tone_ana import service as tone_serv

logger.remove()
logger.add(sys.stderr, level="INFO")

# 加载总配置文件
DEFAULT_GLOBAL_CONFIG_PATH = R'config/global_config.yaml'
g_config = load_global_config(DEFAULT_GLOBAL_CONFIG_PATH)

if __name__ == '__main__':
    try:
        # 线程列表
        thread_list = []

        # 加载服务配置文件
        bilibili_live_config = load_bilibili_live_config(g_config)
        screenshot_config = load_screenshot_config(g_config)
        blip_config = load_blip_image_captioning_large_config(g_config)
        gpt_sovits_config = load_gpt_sovits_config(g_config)
        tone_analysis_service_config = load_tone_analysis_service_config(g_config)
        obs_config = load_obs_config(g_config)
        chatglm3_service_config = load_chatglm3_service_config(g_config)
        asr_service_config = load_asr_config(g_config)
        vad_config = load_vad_config(g_config)
        zerolan_live_robot_config = load_zerolan_live_robot_config(g_config)

        # 初始化服务（赋初值 / 加载模型）
        assert bili_serv.init(*bilibili_live_config)
        assert scrn_serv.init(*screenshot_config)
        assert blip_serv.init(*blip_config)
        assert gptsovits_serv.init(*gpt_sovits_config)
        assert tone_serv.init(*tone_analysis_service_config)
        assert obs_serv.init(*obs_config)
        assert vad.service.init(*vad_config)
        assert asr.service.init(*asr_service_config)
        assert controller.service.init(*zerolan_live_robot_config)

        # 启动弹幕监听服务
        bili_thread = threading.Thread(target=bili_serv.start)
        thread_list.append(bili_thread)
        bili_thread.start()

        # 启动播放器线程
        audio_play_thread = threading.Thread(target=audio_player.service.start)
        thread_list.append(audio_play_thread)
        audio_play_thread.start()

        # 启动 Minecraft 游戏事件监听线程
        minecraft_thread = threading.Thread(target=minecraft.py.service.start)
        thread_list.append(minecraft_thread)
        minecraft_thread.start()

        # 启动 VAD 服务线程
        vad_serv_thread = threading.Thread(target=vad.service.start)
        thread_list.append(vad_serv_thread)
        vad_serv_thread.start()

        # 启动 ASR 服务线程
        asr_serv_thread = threading.Thread(target=asr.service.start)
        thread_list.append(asr_serv_thread)
        asr_serv_thread.start()

        # 启动控制器
        ctrl_thread = threading.Thread(target=controller.service.start)
        thread_list.append(ctrl_thread)
        ctrl_thread.start()

        # 启动生命周期
        asyncio.run(service_start())

        # 等待所有线程结束
        for thread in thread_list:
            thread.join()

    except Exception as e:
        logger.exception(e)
        logger.critical(f'💥 Zerolan Live Robot 因无法处理的异常而退出')
