import os.path

import livestream.bilibili.service
from config import ASRConfig, ImageCaptioningConfig, LargeLanguageModelConfig, TextToSpeechConfig
from config import GLOBAL_CONFIG as G_CFG
from config import LiveStreamConfig
from utils.datacls import ServiceNameRegistry as SNR, Platform


def start_asr(config: ASRConfig):
    debug, host, port = config.debug, config.host, config.port
    assert len(config.models) > 0, f'At least 1 ASR model should configurate.'
    model = config.models[0]
    if model == SNR.PARAFORMER:
        model_path = model.get('model_path', None)
        version = model.get('version', None)
        assert os.path.exists(model_path), f'Model path "{model_path}" does not exist.'

        import asr.app

        asr.app.start(model_path=model_path, host=host, port=port, debug=debug, version=version)


def start_img_cap(config: ImageCaptioningConfig):
    debug, host, port = config.debug, config.host, config.port
    assert len(config.models) > 0, f'At least 1 Image-Captioning model should configurate.'
    model = config.models[0]
    if model == SNR.BLIP:
        model_path = model.get('model_path', None)
        assert os.path.exists(model_path), f'Model path "{model_path}" does not exist.'

        import blip_img_cap.app

        blip_img_cap.app.start(model_path=model_path, host=host, port=port, debug=debug)


def start_llm(config: LargeLanguageModelConfig):
    debug, host, port = config.debug, config.host, config.port
    assert len(config.models) > 0, f'At least 1 LLM model should configurate.'
    model = config.models[0]
    if model == SNR.CHATGLM3:
        model_path = model.get('model_path', None)
        assert os.path.exists(model_path), f'Model path "{model_path}" does not exist.'

        quantize = model.get('quantize', None)
        if quantize:
            assert quantize in [4, 8], f'{model} should be quantized by 4 or 8, not {quantize}.'

        import llm.chatglm3.app

        llm.chatglm3.app.start(model_path, quantize, host, port, debug)
    elif model == SNR.QWEN:
        model_path = model.get('model_path', None)
        assert os.path.exists(model_path), f'Model path "{model_path}" does not exist.'

        loading_mode = model.get('loading_mode', 'auto')

        import llm.qwen.app

        llm.qwen.app.start(model_path, loading_mode, host, port, debug)
    elif model == SNR.YI:
        model_path = model.get('model_path', None)
        assert os.path.exists(model_path), f'Model path "{model_path}" does not exist.'

        loading_mode = model.get('loading_mode', 'auto')

        import llm.yi_6b.app

        llm.yi_6b.app.start(model_path, loading_mode, host, port, debug)
    elif model == SNR.SHISA:
        import llm.shisa.app
        model_path = model.get('model_path', None)
        assert os.path.exists(model_path), f'Model path "{model_path}" does not exist.'

        llm.shisa.app.start(model_path, host, port, debug)


def start_tts(config: TextToSpeechConfig):
    debug, host, port = config.debug, config.host, config.port
    save_dir = config.save_directory
    assert os.path.exists(save_dir), f'Save directory "{save_dir}" does not exist.'
    assert len(config.models) > 0, f'At least 1 LLM model should configurate.'
    model = config.models[0]
    if model == SNR.GPT_SOVITS:
        pass


def live_stream_start(config: LiveStreamConfig):
    assert len(config.platforms) > 0, f'At least 1 live stream platform should configurate.'
    platform = config.platforms[0]
    if platform.get(Platform.BILIBILI, None):
        bili_cfg = platform[Platform.BILIBILI]
        sessdata, bili_jct, buvid3, room_id = bili_cfg['sessdata'], bili_cfg['bili_jct'], bili_cfg[
            'buvid3'], bili_cfg['room_id'],
        livestream.bilibili.service.start(sessdata, bili_jct, buvid3, room_id)
    else:
        raise NotImplementedError(f'Do not support live stream platform "{config.platforms}".')


def start():
    assert G_CFG.large_language_model.enable, f'LLM service must be enabled.'
    start_llm(G_CFG.large_language_model)

    if G_CFG.auto_speech_recognition.enable:
        start_asr(G_CFG.auto_speech_recognition)

    if G_CFG.image_captioning.enable:
        start_img_cap(G_CFG.image_captioning)

    if G_CFG.text_to_speech.enable:
        start_tts(G_CFG.text_to_speech)
