import pyautogui
import pygetwindow as gw
from PIL.Image import Image
from loguru import logger

from common.utils import file_util


class Screen:

    @staticmethod
    def capture(win_title: str, k: float = 1.0) -> (Image, str):
        # Get the window
        win_list = gw.getWindowsWithTitle(win_title)
        assert len(win_list) != 0, f'Window capture failed: Can not find {win_title}'
        w = win_list[0]
        # Activate the window
        w.activate()
        # Calculate the screen region
        region = (
            w.centerx - k * w.width / 2, w.centery - k * w.height / 2, w.centerx + k * w.width / 2,
            w.centery + k * w.height / 2)
        region = tuple(int(num * k) for num in region)

        assert hasattr(pyautogui, "screenshot")
        # Note: If you have a problem that the screenshot cannot be found, try updating the `pyautogui` library
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
                logger.warning("Window capture failed: Taking a screenshot in a split-screen situation may cause problems, please try placing the target window on the home screen.")
        except AssertionError as e:
            logger.warning(e)
        except gw.PyGetWindowException as e:
            if "Error code from Windows: 0" in str(e):
                logger.warning("Window capture failed: Lost focus. Is your target window activated?")
        except Exception as e:
            logger.exception(e)
            logger.warning("Window capture failed: Unknown error.")
        return None, None
