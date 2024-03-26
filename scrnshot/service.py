import os.path
import time
from os import PathLike

import pyautogui
import pygetwindow as gw
from loguru import logger

from config.global_config import ScreenshotConfig

is_initialized = False

K = 0.9
SAVE_PATH = '.tmp/screenshots'
WIN_TITLE = None


def init(config: ScreenshotConfig):
    logger.info('📷️ 截图服务初始化中……')
    global K, SAVE_PATH, WIN_TITLE, is_initialized
    K = config.k
    WIN_TITLE = config.win_title
    SAVE_PATH = config.save_dir
    is_initialized = True
    logger.info('📷️ 截图服务初始化完毕')
    return is_initialized


def screen_cap():
    try:
        # 获取窗口
        win_list = gw.getWindowsWithTitle(WIN_TITLE)
        if len(win_list) == 0:
            logger.warning(f'无法找到窗口 {WIN_TITLE}')
            return None
        w = win_list[0]
        # 激活窗口
        w.activate()
        # 计算屏幕位置
        region = (w.centerx - K * w.width / 2, w.centery - K * w.height / 2, w.centerx + K * w.width / 2,
                  w.centery + K * w.height / 2)
        region = tuple(int(num * K) for num in region)
        # 截图
        img = pyautogui.screenshot(region=region)
        img_save_path = os.path.join(SAVE_PATH, f'{time.time()}.png')
        img.save(img_save_path)
        return img_save_path
    except Exception as e:
        logger.error(f'窗口 {WIN_TITLE} 捕获失败')
        return None
