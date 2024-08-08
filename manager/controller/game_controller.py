from abc import ABC

import pyautogui

from common.exception.unsafe_exception import UnsafeOperationException


class AbstractGameController(ABC):
    def __init__(self):
        # pyautogui.FAILSAFE 不应为 False
        if not pyautogui.FAILSAFE:
            raise UnsafeOperationException(
                "pyautogui 的故障保护现在被关闭，这极有可能造成程序无法退出对键盘、鼠标等设备的控制，从而导致您失去对计算机的控制。"
                "本程序只能在故障保护被开启的条件下启动。")
        pass

    def start(self):
        pass
