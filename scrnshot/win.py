import os.path
import time

import pyautogui
import pygetwindow as gw
import yaml
from loguru import logger


def load_config():
    with open(file=r'scrnshot/config.yaml', encoding='utf-8', mode='r') as file:
        config = yaml.safe_load(file)
        config = config.get('ScreenshotConfig', {})
        k = config.get('k', 0.9)
        save_path = config.get('save_path')
        win_title = config.get('win_title')
        if os.path.exists(save_path):
            return k, save_path, win_title
        return k, '.tmp/screenshots', win_title


k, save_path, win_title = load_config()


def screen_cap():
    try:
        # 获取窗口
        win_list = gw.getWindowsWithTitle(win_title)
        if len(win_list) == 0:
            logger.error(f'无法找到窗口 {win_title}')
            return None
        w = win_list[0]
        # 激活窗口
        w.activate()
        # 计算屏幕位置
        region = (w.centerx - k * w.width / 2, w.centery - k * w.height / 2, w.centerx + k * w.width / 2,
                  w.centery + k * w.height / 2)
        region = tuple(int(num * k) for num in region)
        # 截图
        img = pyautogui.screenshot(region=region)

        img.save(os.path.join(save_path, f'{time.time()}.png'))
        return img
    except Exception as e:
        return None
