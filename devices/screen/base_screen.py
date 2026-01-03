from abc import ABC, abstractmethod
import platform

from PIL.Image import Image


class BaseScreen(ABC):
    @abstractmethod
    def safe_capture(self, win_title: str = None, k: float = 1.0) -> (Image, str):
        pass


class Screen:
    def __init__(self):
        if platform.system() == "Windows":
            from devices.screen.win_screen import WindowsScreen
            self._screen = WindowsScreen()
        else:
            from devices.screen.linux_screen import LinuxScreen
            self._screen = LinuxScreen()

    def safe_capture(self, win_title: str = None, k: float = 1.0) -> (Image, str):
        return self._screen.safe_capture(win_title, k)
