import platform
from abc import ABC, abstractmethod

from PIL.Image import Image

import devices.headless


class BaseScreen(ABC):
    @abstractmethod
    def safe_capture(self, win_title: str = None, k: float = 1.0) -> (Image, str):
        pass


class Screen:
    def __init__(self):
        self._headless = devices.headless.is_headless()
        if not self._headless:
            if platform.system() == "Windows":
                from devices.screen.win_screen import WindowsScreen
                self._screen = WindowsScreen()
            else:
                from devices.screen.linux_screen import LinuxScreen
                self._screen = LinuxScreen()
        else:
            raise Exception("Screenshot on a headless system is not supported.")

    def safe_capture(self, win_title: str = None, k: float = 1.0) -> (Image, str):
        if not self._headless:
            return self._screen.safe_capture(win_title, k)
        else:
            raise Exception("Screenshot on a headless system is not supported.")
