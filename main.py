import asyncio
import sys
import threading

from loguru import logger

from minecraft.app import MinecraftApp
import service_starter
from config import GLOBAL_CONFIG as G_CFG
from controller.app import ControllerApp
from lifecycle import LifeCycle
from obs.service import ObsService
from vad.service import VADService

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
            from asr import ASRService

            asr_service = ASRService()
            thread_list.append(threading.Thread(target=asr_service.start))

        if G_CFG.voice_activity_detection.enable:
            # VAD 服务线程
            vad_service = VADService(G_CFG)
            thread_list.append(threading.Thread(target=vad_service.start))

        if G_CFG.obs.enable:
            obs_service = ObsService(G_CFG)

        if G_CFG.text_to_speech.enable:
            # 播放器线程
            from audio_player.service import AudioPlayerService

            audio_player_service = AudioPlayerService(obs_service)
            thread_list.append(threading.Thread(target=audio_player_service.start))

        if G_CFG.minecraft.enable:
            # Minecraft 游戏事件监听线程
            minecraft_app = MinecraftApp(G_CFG)
            thread_list.append(threading.Thread(target=minecraft_app.start))

        # Life cycle
        life_cycle = LifeCycle(cfg=G_CFG, asr_service=asr_service, audio_player_service=audio_player_service)

        # 控制器线程
        controller_app = ControllerApp(cfg=G_CFG, lifecycle=life_cycle, audio_player_service=audio_player_service)
        thread_list.append(threading.Thread(target=controller_app.start))

        # 启动所有线程
        for thread in thread_list:
            thread.start()

        # 启动生命周期
        asyncio.run(life_cycle.start())

        # 等待所有线程结束
        for thread in thread_list:
            thread.join()

    except Exception as e:
        logger.exception(e)
        logger.critical(f'💥 Zerolan Live Robot 因无法处理的异常而退出')
