import argparse

from loguru import logger

from common.abs_service import AbstractService
from config import ASRConfig, ImageCaptioningConfig, LLMServiceConfig, TextToSpeechConfig, GlobalConfig
from config import GLOBAL_CONFIG as G_CFG
from utils.datacls import ServiceNameConst as SNC, PlatformConst


def start_asr(config: ASRConfig):
    model = config.models[0]
    if SNC.PARAFORMER == model.model_name:
        from asr.speech_paraformer.app import SpeechParaformerApp

        SpeechParaformerApp(config).start()


def start_img_cap(config: ImageCaptioningConfig):
    model = config.models[0]
    if SNC.BLIP == model.model_name:
        from img_cap.blip.app import BlipApp

        BlipApp(config).start()


def start_llm(config: LLMServiceConfig):
    debug, host, port = config.debug, config.host, config.port
    model = config.models[0]
    if SNC.CHATGLM3 == model.model_name:
        import llm.chatglm3.app

        llm.chatglm3.app.start(model.model_path, model.quantize, host, port, debug)
    elif SNC.QWEN == model.model_name:
        import llm.qwen.app

        llm.qwen.app.start(model.model_path, model.loading_mode, host, port, debug)
    elif SNC.YI == model.model_name:
        import llm.yi_6b.app

        llm.yi_6b.app.start(model.model_path, model.loading_mode, host, port, debug)
    elif SNC.SHISA == model.model_name:
        import llm.shisa.app

        llm.shisa.app.start(model.model_path, host, port, debug)


def start_tts(config: TextToSpeechConfig):
    model = config.models[0]
    if SNC.GPT_SOVITS == model.model_name:
        pass


def get_live_stream_service(config: GlobalConfig) -> AbstractService:
    platform = config.live_stream.platforms[0]
    if platform.platform_name == PlatformConst.BILIBILI:
        from livestream.bilibili.service import BilibiliService
        return BilibiliService(config)


def start():
    processes = []

    return processes


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--service', '-s', type=str)
    args = parser.parse_args()
    if 'asr' == args.service:
        if G_CFG.auto_speech_recognition.enable:
            start_asr(G_CFG.auto_speech_recognition)
        else:
            logger.warning('ASR service is not allowed to start: Check your configuration file.')
    elif 'llm' == args.service:
        if G_CFG.large_language_model.enable:
            start_llm(G_CFG.large_language_model)
        else:
            logger.warning('LLM service is not allowed to start: Check your configuration file.')
    elif 'ic' == args.service:
        if G_CFG.image_captioning.enable:
            start_img_cap(G_CFG.image_captioning)
        else:
            logger.warning('Image-captioning service is not allowed to start: Check your configuration file.')
    elif 'tts' == args.service:
        if G_CFG.text_to_speech.enable:
            start_tts(G_CFG.text_to_speech)
        else:
            logger.warning('TTS service is not allowed to start: Check your configuration file.')
    else:
        raise NotImplementedError(f'{args.service} service is not supported.')
