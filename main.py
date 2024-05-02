import asyncio
import sys
import threading

from loguru import logger

import asr.service
import audio_player.service
import controller.app
import lifecycle
import livestream.bilibili.service
import service_starter
import tone_ana.service
import vad.service
from common.datacls import PlatformConst as PC
from common.exc import InitError
from config import GLOBAL_CONFIG as G_CFG

logger.remove()
logger.add(sys.stderr, level="INFO")

live_stream_platform_name = G_CFG.live_stream.platforms[0].platform_name

if __name__ == '__main__':
    try:
        audio_player.service.init()
        vad.service.init()
        asr.service.init()
        tone_ana.service.init()
        controller.app.init()
        lifecycle.init()

        # Thread list for all services
        thread_list = []

        # Live stream service thread
        if PC.BILIBILI == live_stream_platform_name:
            livestream.bilibili.service.init()
            thread_list.append(threading.Thread(target=livestream.bilibili.service.start))
        else:
            raise NotImplementedError(f'Unsupported live stream platform: {live_stream_platform_name}')
        # thread_list.append(threading.Thread(target=service_starter.start_live_stream_service))

        # VAD service thread
        thread_list.append(threading.Thread(target=vad.service.start))

        # ASR service thread
        thread_list.append(threading.Thread(target=asr.service.start))

        # Audio player thread
        thread_list.append(threading.Thread(target=audio_player.service.start))

        # Minecraft
        thread_list.append(threading.Thread(target=service_starter.start_minecraft_service))

        # Controller app thread
        thread_list.append(threading.Thread(target=controller.app.start))

        # Start all threads
        for thread in thread_list:
            thread.start()

        # Start lifecycle
        asyncio.run(lifecycle.start())

        # Wait for all threads finishing
        for thread in thread_list:
            thread.join()
    except InitError as e:
        logger.exception(e)
        logger.critical('❌️ ' + e.message)
    except Exception as e:
        logger.exception(e)
        logger.critical(f'😭 Zerolan Live Robot exited: Unhandled exception.')
