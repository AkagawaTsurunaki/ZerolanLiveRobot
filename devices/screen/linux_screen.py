from PIL.Image import Image

from devices.screen.base_screen import BaseScreen


class LinuxScreen(BaseScreen):
    def __init__(self):
        super().__init__()

    def safe_capture(self, win_title: str = None, k: float = 1.0) -> (Image, str):
        raise NotImplementedError("Not supported on Linux.")