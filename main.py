import asyncio
import sys
import threading

from loguru import logger

import asr.service
import audio_player.service
import scrnshot.service
import service_starter
import vad.service
from config import GLOBAL_CONFIG as G_CFG
from lifecycle import LifeCycle
from scrnshot.service import ScreenshotService
from tone_ana.service import ToneAnalysisService

logger.remove()
logger.add(sys.stderr, level="INFO")

if __name__ == '__main__':
    try:
        audio_player.service.init()
        vad.service.init()
        scrnshot.service.init()
        asr.service.init()

        # Thread list for all services
        thread_list = []

        # Live stream service thread
        thread_list.append(threading.Thread(target=service_starter.start_live_stream_service))

        # VAD service thread
        thread_list.append(threading.Thread(target=vad.service.start))

        # ASR service thread
        thread_list.append(threading.Thread(target=asr.service.start))

        # Audio player thread
        thread_list.append(threading.Thread(target=audio_player.service.start))

        # Minecraft
        thread_list.append(threading.Thread(target=service_starter.start_minecraft_service))

        # Life cycle
        life_cycle = LifeCycle(cfg=G_CFG,
                               asr_service=asr_service,
                               audio_player_service=audio_player_service,
                               obs_service=obs_service,
                               tone_ana_service=tone_analysis_service,
                               screenshot_service=scrnshot_service)

        # Controller app thread

        thread_list.append(threading.Thread(target=controller_app.start))

        # Start all threads
        for thread in thread_list:
            thread.start()

        # Start lifecycle
        asyncio.run(life_cycle.start())

        # Wait for all threads finishing
        for thread in thread_list:
            thread.join()

    except Exception as e:
        logger.exception(e)
        logger.critical(f'Zerolan Live Robot exited: Unhandled exception.')
