import asyncio
import sys
import threading

from loguru import logger

import asr.service
import controller.app
import minecraft.app
import service_starter
import vad.service
from config import GLOBAL_CONFIG as G_CFG
from lifecircle import start_cycle

logger.remove()
logger.add(sys.stderr, level="INFO")

if __name__ == '__main__':
    try:

        # 线程列表
        thread_list = []

        # 弹幕监听服务
        if G_CFG.live_stream.enable:
            thread_list.append(threading.Thread(target=service_starter.live_stream_start))

        if G_CFG.auto_speech_recognition.enable:
            # ASR 线程
            thread_list.append(threading.Thread(target=asr.service.start))

        if G_CFG.voice_activity_detection.enable:
            # VAD 服务线程
            thread_list.append(threading.Thread(target=vad.service.start))

        if G_CFG.text_to_speech.enable:
            # 播放器线程
            from audio_player.service import AudioPlayerService

            audio_player_service = AudioPlayerService()
            thread_list.append(threading.Thread(target=audio_player_service.start))

        if G_CFG.minecraft.enable:
            # Minecraft 游戏事件监听线程
            thread_list.append(threading.Thread(target=minecraft.app.start))

        # 控制器线程
        thread_list.append(threading.Thread(target=controller.app.start))

        # 启动所有线程
        for thread in thread_list:
            thread.start()

        # 启动生命周期
        asyncio.run(start_cycle())

        # 等待所有线程结束
        for thread in thread_list:
            thread.join()

    except Exception as e:
        logger.exception(e)
        logger.critical(f'💥 Zerolan Live Robot 因无法处理的异常而退出')
