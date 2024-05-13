import pyautogui
import pygetwindow
import pygetwindow as gw
from PIL.Image import Image
from loguru import logger

from config import GLOBAL_CONFIG as G_CFG

_k: float = G_CFG.screenshot.k
_save_path: str = G_CFG.screenshot.save_directory
_win_title: str = G_CFG.screenshot.window_title


def screen_cap() -> Image | None:
    try:
        # 获取窗口
        win_list = gw.getWindowsWithTitle(_win_title)
        assert len(win_list) != 0, f'⚠️ 无法捕获窗口：找不到 {_win_title}'
        w = win_list[0]
        # 激活窗口
        w.activate()
        # 计算屏幕位置
        region = (
            w.centerx - _k * w.width / 2, w.centery - _k * w.height / 2, w.centerx + _k * w.width / 2,
            w.centery + _k * w.height / 2)
        region = tuple(int(num * _k) for num in region)
        # 截图
        assert hasattr(pyautogui, "screenshot")
        # Note: 可能出现找不到 screenshot 的问题, 请更新 pyautogui 库
        img = pyautogui.screenshot(region=region)

        return img

        # img_save_path = os.path.join(_save_path, f'{time.time()}.png')
        # img.save(img_save_path)
        # return img_save_path
    except ValueError as e:
        if str(e) == "Coordinate 'right' is less than 'left'":
            logger.warning("⚠️ 窗口捕获失败：分屏情况下截屏可能会出现问题，请尝试将目标窗口放置于主屏幕。")
    except AssertionError as e:
        logger.warning(e)
    except pygetwindow.PyGetWindowException as e:
        if "Error code from Windows: 0" in str(e):
            logger.warning("⚠️ 窗口捕获失败：失去画面焦点。")
    except Exception as e:
        logger.exception(e)
        logger.warning("⚠️ 窗口捕获失败：未知错误。")

