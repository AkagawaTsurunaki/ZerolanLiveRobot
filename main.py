import asyncio
import sys
import threading

from flask import Flask
from loguru import logger

import audio_player.service
from bilibili import service as bili_serv
from blip_img_cap import service as blip_serv
from gptsovits import service as gptsovits_serv
from initzr import load_global_config, load_bilibili_live_config, load_blip_image_captioning_large_config, \
    load_screenshot_config, load_gpt_sovits_config, load_tone_analysis_service_config, load_chatglm3_service_config, \
    load_zerolan_live_robot_config, load_obs_config
from lifecircle import life_circle, init, load_custom_history
from obs import service as obs_serv
from scrnshot import service as scrn_serv
from tone_ana import service as tone_serv

FLAG = True
DEFAULT_GLOBAL_CONFIG_PATH = R'config/global_config.yaml'
logger.remove()
logger.add(sys.stderr, level="INFO")

app = Flask(__name__)
g_config = load_global_config(DEFAULT_GLOBAL_CONFIG_PATH)


@app.route('/reset', methods=['GET'])
def reset():
    load_custom_history()
    return 'OK'


async def service_start():
    logger.info('💜 ZerolanLiveRobot，启动！')
    while FLAG:
        await life_circle()
        await asyncio.sleep(1)

if __name__ == '__main__':
    # 加载配置文件
    # try:

    bilibili_live_config = load_bilibili_live_config(g_config)
    screenshot_config = load_screenshot_config(g_config)
    blip_config = load_blip_image_captioning_large_config(g_config)
    gpt_sovits_config = load_gpt_sovits_config(g_config)
    tone_analysis_service_config = load_tone_analysis_service_config(g_config)
    zerolan_live_robot_config = load_zerolan_live_robot_config(g_config)
    obs_config = load_obs_config(g_config)
    chatglm3_service_config = load_chatglm3_service_config(g_config)

    # 启动弹幕监听服务

    assert bili_serv.init(*bilibili_live_config)
    bili_thr = threading.Thread(target=bili_serv.start)
    bili_thr.start()

    # 初始化服务（赋初值 / 加载模型）

    assert scrn_serv.init(*screenshot_config)
    assert blip_serv.init(*blip_config)
    assert gptsovits_serv.init(*gpt_sovits_config)
    assert tone_serv.init(*tone_analysis_service_config)
    assert obs_serv.init(*obs_config)
    assert init(*zerolan_live_robot_config)

    # 启动播放器线程
    audio_play_thread = threading.Thread(target=audio_player.service.start)
    audio_play_thread.start()

    # 主控制器线程
    app_thread = threading.Thread(target=app.run, args=('127.0.0.1', 11451, False))
    app_thread.start()

    # 启动生命周期
    asyncio.run(service_start())

    bili_thr.join()
    audio_play_thread.join()
    app_thread.join()
# except Exception:
#     logger.critical(f'💥 ZEROLAN LIVE ROBOT 初始化失败：因无法处理的异常而退出')
