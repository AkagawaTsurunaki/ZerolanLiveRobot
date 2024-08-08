import time
from dataclasses import dataclass
from typing import List

import pyautogui
from dataclasses_json import dataclass_json
from loguru import logger

from manager.controller.game_controller import AbstractGameController

pyautogui.FAILSAFE = True


@dataclass_json
@dataclass
class MinecraftKeyboardOperation:
    description: str
    keys: List[str]
    keywords: List[str]


class MinecraftController(AbstractGameController):
    def __init__(self):
        super().__init__()
        self.keyboard_operations: List[MinecraftKeyboardOperation] = [
            MinecraftKeyboardOperation(keys=["w"], keywords=["前进", "前"], description="向前行走"),
            MinecraftKeyboardOperation(keys=["s"], keywords=["后退", "后"], description="向后行走"),
            MinecraftKeyboardOperation(keys=["a"], keywords=["左"], description="向左行走"),
            MinecraftKeyboardOperation(keys=["d"], keywords=["右"], description="向右行走"),
            MinecraftKeyboardOperation(keys=["shift"], keywords=["潜行", "蹲下"], description="潜行")
        ]

    def get_desc(self, key: str):
        for keyboard_operation in self.keyboard_operations:
            if key in keyboard_operation.keys:
                return keyboard_operation.description
        return None

    def parse_keywords(self, s: str) -> List[str]:
        # TODO: 可能需要大语言模型或者简单的分割模型
        return ["w", "w", "s", "s", "d", "a", "d", "a", "w", "w", "shift", "w"]

    def start(self):
        # actions = ["往前走", "向左走", "往右来", "快往后走", "潜行"]
        # with ProgressToast("AI 正在控制您的计算机...", level="warn", busy=True) as bar:
        keys = self.parse_keywords("TODO")
        for key in keys:
            time.sleep(1)
            logger.info(f"按下键盘: {key}")
            # bar.set_message(f"按下键盘: {self.get_desc(key)}")
            pyautogui.keyDown(key)
            time.sleep(1)
            pyautogui.keyUp(key)
