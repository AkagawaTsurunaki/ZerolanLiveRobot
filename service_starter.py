import argparse

from loguru import logger

import livestream.bilibili.service
from config import ASRConfig, ImageCaptioningConfig, LLMServiceConfig, TextToSpeechConfig, LiveStreamConfig
from config import GLOBAL_CONFIG as G_CFG
from utils.datacls import ServiceNameConst as SNR, PlatformConst


def start_asr(config: ASRConfig):
    model = config.models[0]
    if SNR.PARAFORMER == model.model_name:
        from asr.speech_paraformer.app import SpeechParaformerApp

        SpeechParaformerApp(config).start()


def start_img_cap(config: ImageCaptioningConfig):
    model = config.models[0]
    if SNR.BLIP == model.model_name:
        from img_cap.blip.app import BlipApp

        BlipApp(config).start()


def start_llm(config: LLMServiceConfig):
    debug, host, port = config.debug, config.host, config.port
    model = config.models[0]
    if SNR.CHATGLM3 == model.model_name:
        import llm.chatglm3.app

        llm.chatglm3.app.start(model.model_path, model.quantize, host, port, debug)
    elif SNR.QWEN == model.model_name:
        import llm.qwen.app

        llm.qwen.app.start(model.model_path, model.loading_mode, host, port, debug)
    elif SNR.YI == model.model_name:
        import llm.yi_6b.app

        llm.yi_6b.app.start(model.model_path, model.loading_mode, host, port, debug)
    elif SNR.SHISA == model.model_name:
        import llm.shisa.app

        llm.shisa.app.start(model.model_path, host, port, debug)


def start_tts(config: TextToSpeechConfig):
    model = config.models[0]
    if SNR.GPT_SOVITS == model.model_name:
        pass


def live_stream_start(config: LiveStreamConfig):
    platform = config.platforms[0]
    if platform.platform_name == PlatformConst.BILIBILI:
        room_id, sessdata, bili_jct, buvid3 = platform.room_id, platform.sessdata, platform.bili_jct, platform.buvid3
        livestream.bilibili.service.start(sessdata, bili_jct, buvid3, room_id)


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
