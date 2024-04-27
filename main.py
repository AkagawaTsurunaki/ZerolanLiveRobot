import asyncio
import sys
import threading

from loguru import logger

import service_starter
from asr.service import ASRService
from audio_player.service import AudioPlayerService
from config import GLOBAL_CONFIG as G_CFG
from controller.app import ControllerApp
from lifecycle import LifeCycle
from minecraft.app import MinecraftApp
from obs.service import ObsService
from scrnshot.service import ScreenshotService
from vad.service import VADService
from tone_ana.service import ToneAnalysisService

logger.remove()
logger.add(sys.stderr, level="INFO")

if __name__ == '__main__':
    try:

        # Thread list for all services
        thread_list = []

        # Live stream service thread
        live_stream_serv = service_starter.get_live_stream_service(G_CFG.live_stream)
        thread_list.append(threading.Thread(target=live_stream_serv.start))

        # VAD service thread
        vad_serv = VADService(G_CFG)
        thread_list.append(threading.Thread(target=vad_serv.start))

        # ASR service thread
        asr_service = ASRService(G_CFG, vad_serv)
        thread_list.append(threading.Thread(target=asr_service.start))

        # OBS service (no thread need)
        obs_service = ObsService(G_CFG)

        # Tone analysis service
        tone_analysis_service = ToneAnalysisService(G_CFG)

        # Screenshot service
        scrnshot_service = ScreenshotService(G_CFG)

        audio_player_service = AudioPlayerService(obs_service)
        thread_list.append(threading.Thread(target=audio_player_service.start))

        minecraft_app = MinecraftApp(G_CFG)
        thread_list.append(threading.Thread(target=minecraft_app.start))

        # Life cycle
        life_cycle = LifeCycle(cfg=G_CFG,
                               asr_service=asr_service,
                               audio_player_service=audio_player_service,
                               obs_service=obs_service,
                               tone_ana_service=tone_analysis_service,
                               screenshot_service=scrnshot_service)

        # Controller app thread
        controller_app = ControllerApp(cfg=G_CFG, lifecycle=life_cycle, audio_player_service=audio_player_service)
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
