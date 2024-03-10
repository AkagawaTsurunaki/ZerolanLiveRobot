import asyncio
import sys
import threading

from bilibili import service as bili_serv
from blip_img_cap import service as blip_serv
from chatglm3 import service as chatglm3_serv
from gptsovits import service as gptsovits_serv
from initzr import load_global_config, load_bilibili_live_config, load_blip_image_captioning_large_config, \
    load_screenshot_config, load_gpt_sovits_config, load_tone_analysis_service_config, load_chatglm3_service_config, \
    load_zerolan_live_robot_config, load_obs_config
from scrnshot import service as scrn_serv
from tone_ana import service as tone_serv
from lifecircle import life_circle, init
from obs import service as obs_serv
from loguru import logger

FLAG = True
DEFAULT_GLOBAL_CONFIG_PATH = R'config/global_config.yaml'
logger.remove()
logger.add(sys.stderr, level="INFO")


async def service_start():
    # B站监听弹幕启动
    bi_t = threading.Thread(target=bili_serv.start)
    bi_t.start()
    logger.info('💜 ZerolanLiveRobot，启动！')
    while FLAG:
        await life_circle()
        await asyncio.sleep(1)
    bi_t.join()


if __name__ == '__main__':
    # 加载配置文件

    config = load_global_config(DEFAULT_GLOBAL_CONFIG_PATH)

    bilibili_live_config = load_bilibili_live_config(config)
    screenshot_config = load_screenshot_config(config)
    blip_config = load_blip_image_captioning_large_config(config)
    gpt_sovits_config = load_gpt_sovits_config(config)
    tone_analysis_service_config = load_tone_analysis_service_config(config)
    chatglm3_service_config = load_chatglm3_service_config(config)
    zerolan_live_robot_config = load_zerolan_live_robot_config(config)
    obs_config = load_obs_config(config)

    # 初始化服务（赋初值 / 加载模型）

    assert bili_serv.init(*bilibili_live_config)
    assert scrn_serv.init(*screenshot_config)
    assert blip_serv.init(*blip_config)
    assert gptsovits_serv.init(*gpt_sovits_config)
    assert tone_serv.init(*tone_analysis_service_config)
    assert chatglm3_serv.init(*chatglm3_service_config)
    assert obs_serv.init(*obs_config)
    assert init(*zerolan_live_robot_config)

    asyncio.run(service_start())
