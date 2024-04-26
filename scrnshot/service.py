import os.path
import time

import pyautogui
import pygetwindow as gw
from loguru import logger

from config import GlobalConfig


class ScreenshotService:
    def __init__(self, cfg: GlobalConfig):
        self._k = cfg.screenshot.k
        self._save_path = cfg.screenshot.save_directory
        self._win_title = cfg.screenshot.window_title

    def screen_cap(self):
        try:
            # 获取窗口
            win_list = gw.getWindowsWithTitle(self._win_title)
            if len(win_list) == 0:
                logger.warning(f'Can not find window: {self._win_title}')
                return None
            w = win_list[0]
            # 激活窗口
            w.activate()
            # 计算屏幕位置
            region = (
            w.centerx - self._k * w.width / 2, w.centery - self._k * w.height / 2, w.centerx + self._k * w.width / 2,
            w.centery + self._k * w.height / 2)
            region = tuple(int(num * self._k) for num in region)
            # 截图
            img = pyautogui.screenshot(region=region)
            img_save_path = os.path.join(self._save_path, f'{time.time()}.png')
            img.save(img_save_path)
            return img_save_path
        except Exception as e:
            logger.error(f'Failed to capture window: {self._save_path}')
            return None
