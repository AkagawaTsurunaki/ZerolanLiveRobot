import pyautogui
import pygetwindow as gw
from PIL.Image import Image
from loguru import logger

from common.utils import file_util


class Screen:

    @staticmethod
    def capture(win_title: str, k: float = 1.0) -> (Image, str):
        # 获取窗口
        win_list = gw.getWindowsWithTitle(win_title)
        assert len(win_list) != 0, f'无法捕获窗口：找不到 {win_title}'
        w = win_list[0]
        # 激活窗口
        w.activate()
        # 计算屏幕位置
        region = (
            w.centerx - k * w.width / 2, w.centery - k * w.height / 2, w.centerx + k * w.width / 2,
            w.centery + k * w.height / 2)
        region = tuple(int(num * k) for num in region)

        # 截图
        assert hasattr(pyautogui, "screenshot")
        # 注意: 如果出现找不到 screenshot 的问题, 请尝试更新 pyautogui 库
        img = pyautogui.screenshot(region=region)

        img_save_path = file_util.create_temp_file(prefix="screenshot", suffix=".png", tmpdir="image")
        img.save(img_save_path)

        return img, img_save_path

    @staticmethod
    def screen_cap(win_title: str, k: float = 1.0) -> (Image | None, str | None):
        try:
            return Screen.capture(win_title, k)
        except ValueError as e:
            if str(e) == "Coordinate 'right' is less than 'left'":
                logger.warning("窗口捕获失败：分屏情况下截屏可能会出现问题，请尝试将目标窗口放置于主屏幕。")
        except AssertionError as e:
            logger.warning(e)
        except gw.PyGetWindowException as e:
            if "Error code from Windows: 0" in str(e):
                logger.warning("窗口捕获失败：失去画面焦点。")
        except Exception as e:
            logger.exception(e)
            logger.warning("窗口捕获失败：未知错误。")
        return None, None
