import asyncio
import sys
import threading

from loguru import logger

import asr.service
import audio_player.service
import bilibili.service
import controller.app
import minecraft.app
import vad.service
from lifecircle import service_start

logger.remove()
logger.add(sys.stderr, level="INFO")

if __name__ == '__main__':
    try:
        # 线程列表
        thread_list = []

        # 启动弹幕监听服务
        bili_thread = threading.Thread(target=bilibili.service.start)
        thread_list.append(bili_thread)
        bili_thread.start()

        # 启动播放器线程
        audio_play_thread = threading.Thread(target=audio_player.service.start)
        thread_list.append(audio_play_thread)
        audio_play_thread.start()

        # 启动 Minecraft 游戏事件监听线程
        minecraft_thread = threading.Thread(target=minecraft.app.start)
        thread_list.append(minecraft_thread)
        minecraft_thread.start()

        # 启动 VAD 服务线程
        vad_serv_thread = threading.Thread(target=vad.service.start)
        thread_list.append(vad_serv_thread)
        vad_serv_thread.start()

        # 启动控制器
        ctrl_thread = threading.Thread(target=controller.app.start)
        thread_list.append(ctrl_thread)
        ctrl_thread.start()

        # 启动 ASR 线程
        asr_thread = threading.Thread(target=asr.service.start)
        thread_list.append(asr_thread)
        asr_thread.start()

        # 启动生命周期
        asyncio.run(service_start())

        # 等待所有线程结束
        for thread in thread_list:
            thread.join()

    except Exception as e:
        logger.exception(e)
        logger.critical(f'💥 Zerolan Live Robot 因无法处理的异常而退出')
