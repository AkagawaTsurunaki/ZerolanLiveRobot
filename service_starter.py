import argparse

from loguru import logger


def start_asr():
    from common.config.service_config import ServiceConfig
    config = ServiceConfig.asr_config

    if not config.enable:
        logger.warning("ASR 服务已被禁用：检查您的配置，并将 enable 字段的值改为 True 以启用该服务。")
        return

    from services.asr.app import ASRApplication

    app = ASRApplication()
    app.run()


def start_llm():
    from common.config.service_config import ServiceConfig
    config = ServiceConfig.llm_config

    if not config.enable:
        logger.warning("LLM 服务已被禁用：检查您的配置，并将 enable 字段的值改为 True 以启用该服务。")
        return

    from services.llm.app import LLMApplication

    app = LLMApplication()
    app.run()


def start_img_cap():
    from common.config.service_config import ServiceConfig
    config = ServiceConfig.imgcap_config

    if not config.enable:
        logger.warning("图像字幕服务已被禁用：检查您的配置，并将 enable 字段的值改为 True 以启用该服务。")
        return

    from services.img_cap.app import ImgCapApplication
    app = ImgCapApplication()
    app.run()


def start_tts():
    pass


def start_ocr():
    from common.config.service_config import ServiceConfig
    config = ServiceConfig.ocr_config

    if not config.enable:
        logger.warning("光学字符识别服务已被禁用：检查您的配置，并将 enable 字段的值改为 True 以启用该服务。")
        return

    from services.ocr.app import OCRApplication
    app = OCRApplication()
    app.run()


def start_vidcap():
    from common.config.service_config import ServiceConfig
    config = ServiceConfig.vidcap_config

    if not config.enable:
        logger.warning("视频字幕服务已被禁用：检查您的配置，并将 enable 字段的值改为 True 以启用该服务。")
        return

    from services.vid_cap.app import VidCapApplication
    app = VidCapApplication()
    app.run()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--service', '-s', type=str)
    args = parser.parse_args()
    if 'asr' == args.service:
        return start_asr
    elif 'llm' == args.service:
        return start_llm
    elif 'img_cap' == args.service:
        return start_img_cap
    elif 'tts' == args.service:
        return start_tts
    elif 'ocr' == args.service:
        return start_ocr
    elif 'vid_cap' == args.service:
        return start_vidcap
    else:
        raise NotImplementedError(f'不支持的服务参数：{args.service}')


if __name__ == '__main__':
    import os
    
    import sys
    sys.path.append("")
    logger.debug(f"当前工作目录：{os.getcwd()}")
    run_func = parse_args()
    run_func()
