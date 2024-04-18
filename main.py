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

        # 弹幕监听服务
        thread_list.append(threading.Thread(target=bilibili.service.start))

        # 播放器线程
        thread_list.append(threading.Thread(target=audio_player.service.start))

        # Minecraft 游戏事件监听线程
        thread_list.append(threading.Thread(target=minecraft.app.start))

        # VAD 服务线程
        thread_list.append(threading.Thread(target=vad.service.start))

        # ASR 线程
        thread_list.append(threading.Thread(target=asr.service.start))

        # 控制器线程
        thread_list.append(threading.Thread(target=controller.app.start))

        # 启动所有线程
        for thread in thread_list:
            thread.start()

        # 启动生命周期
        asyncio.run(service_start())

        # 等待所有线程结束
        for thread in thread_list:
            thread.join()

    except Exception as e:
        logger.exception(e)
        logger.critical(f'💥 Zerolan Live Robot 因无法处理的异常而退出')
