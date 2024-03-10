import os.path
import time
from os import PathLike

import pyautogui
import pygetwindow as gw
from loguru import logger

is_initialized = False

K = 0.9
SAVE_PATH = '.tmp/screenshots'
WIN_TITLE = None


def init(win_title: str, k: int, save_dir: str | PathLike):
    logger.info('📷️ 截图服务初始化中……')
    global K, SAVE_PATH, WIN_TITLE, is_initialized
    K = k
    WIN_TITLE = win_title
    SAVE_PATH = save_dir
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

        img.save(os.path.join(SAVE_PATH, f'{time.time()}.png'))
        return img
    except Exception as e:
        return None
