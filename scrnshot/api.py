import os.path
import time

import pyautogui
import pygetwindow as gw
from loguru import logger

from config import GLOBAL_CONFIG as G_CFG

_k: float = G_CFG.screenshot.k
_save_path: str = G_CFG.screenshot.save_directory
_win_title: str = G_CFG.screenshot.window_title


def screen_cap():
    try:
        # 获取窗口
        win_list = gw.getWindowsWithTitle(_win_title)
        if len(win_list) == 0:
            logger.warning(f'Can not find window: {_win_title}')
            return None
        w = win_list[0]
        # 激活窗口
        w.activate()
        # 计算屏幕位置
        region = (
            w.centerx - _k * w.width / 2, w.centery - _k * w.height / 2, w.centerx + _k * w.width / 2,
            w.centery + _k * w.height / 2)
        region = tuple(int(num * _k) for num in region)
        # 截图
        img = pyautogui.screenshot(region=region)
        img_save_path = os.path.join(_save_path, f'{time.time()}.png')
        img.save(img_save_path)
        return img_save_path
    except Exception as e:
        logger.error(f'Failed to capture window: {_save_path}')
        return None
