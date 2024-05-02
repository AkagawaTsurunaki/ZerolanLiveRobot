import argparse

from loguru import logger

from common.datacls import ModelNameConst as MNC, PlatformConst
from config import GLOBAL_CONFIG as G_CFG


def start_asr(model_name: str):
    if MNC.PARAFORMER == model_name:
        import asr.speech_paraformer.app
        asr.speech_paraformer.app.init()
        asr.speech_paraformer.app.start()


def start_img_cap(model_name: str):
    if MNC.BLIP == model_name:
        import img_cap.blip.app
        img_cap.blip.app.init()
        img_cap.blip.app.start()


def start_llm(model_name: str):
    if MNC.CHATGLM3 == model_name:
        import llm.chatglm3.app
        llm.chatglm3.app.init(G_CFG)
        llm.chatglm3.app.start()
    elif MNC.QWEN == model_name:
        import llm.qwen.app
        llm.qwen.app.init(G_CFG)
        llm.qwen.app.start()
    elif MNC.YI == model_name:
        import llm.yi_6b.app
        llm.yi_6b.app.init(G_CFG)
        llm.yi_6b.app.start()
    elif MNC.SHISA == model_name:
        import llm.shisa.app
        llm.shisa.app.init(G_CFG)
        llm.shisa.app.start()


def start_tts(model_name: str):
    if MNC.GPT_SOVITS == model_name:
        logger.warning('No need to start app...')


def start_live_stream_service():
    platform_name = G_CFG.live_stream.platforms[0].platform_name
    if PlatformConst.BILIBILI == platform_name:
        import livestream.bilibili.service
        livestream.bilibili.service.init(G_CFG)
        livestream.bilibili.service.start()


def start_minecraft_service():
    import minecraft.app
    minecraft.app.start(G_CFG)


def start_controller_service():
    import controller.app
    controller.app.init()


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
