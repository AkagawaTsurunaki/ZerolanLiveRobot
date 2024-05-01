import argparse

from loguru import logger

from common.abs_service import AbstractService
from common.datacls import ServiceNameConst as SNC, PlatformConst
from config import GLOBAL_CONFIG as G_CFG
from config import GlobalConfig


def start_asr(model_name: str):
    if SNC.PARAFORMER == model_name:
        import asr.speech_paraformer.app
        asr.speech_paraformer.app.start()


def start_img_cap(model_name: str):
    if SNC.BLIP == model_name:
        import img_cap.blip.app
        img_cap.blip.app.start()


def start_llm(model_name: str):
    if SNC.CHATGLM3 == model_name:
        import llm.chatglm3.app
        llm.chatglm3.app.init(G_CFG)
        llm.chatglm3.app.start()
    elif SNC.QWEN == model_name:
        import llm.qwen.app
        llm.qwen.app.init(G_CFG)
        llm.qwen.app.start()
    elif SNC.YI == model_name:
        import llm.yi_6b.app
        llm.yi_6b.app.init(G_CFG)
        llm.yi_6b.app.start()
    elif SNC.SHISA == model_name:
        import llm.shisa.app
        llm.shisa.app.init(G_CFG)
        llm.shisa.app.start()


def start_tts(model_name: str):
    if SNC.GPT_SOVITS == model_name:
        logger.warning('No need to start app...')


def get_live_stream_service(config: GlobalConfig) -> AbstractService:
    platform = config.live_stream.platforms[0]
    if platform.platform_name == PlatformConst.BILIBILI:
        from livestream.bilibili.service import BilibiliService
        return BilibiliService(config)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--service', '-s', type=str)
    args = parser.parse_args()
    if 'asr' == args.service:
        if G_CFG.auto_speech_recognition.enable:
            start_asr(G_CFG.auto_speech_recognition.models[0].model_name)
        else:
            logger.warning('ASR service is not allowed to start: Check your configuration file.')
    elif 'llm' == args.service:
        if G_CFG.large_language_model.enable:
            start_llm(G_CFG.large_language_model.models[0].model_name)
        else:
            logger.warning('LLM service is not allowed to start: Check your configuration file.')
    elif 'ic' == args.service:
        if G_CFG.image_captioning.enable:
            start_img_cap(G_CFG.image_captioning.models[0].model_name)
        else:
            logger.warning('Image-captioning service is not allowed to start: Check your configuration file.')
    elif 'tts' == args.service:
        if G_CFG.text_to_speech.enable:
            start_tts(G_CFG.text_to_speech.models[0].model_name)
        else:
            logger.warning('TTS service is not allowed to start: Check your configuration file.')
    else:
        raise NotImplementedError(f'{args.service} service is not supported.')
