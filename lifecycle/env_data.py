import json
from dataclasses import dataclass

from common.buffer.game_buf import MinecraftGameEvent
from common.interpretable import Interpretable
from common.utils.str_util import is_blank
from services.live_stream.pipeline import Danmaku


@dataclass
class CustomLiveStreamData(Interpretable):
    dev_say: str
    danmaku: Danmaku
    game_scene: str
    game_event: MinecraftGameEvent | None

    def interpret(self) -> str:
        result = dict()
        if self.dev_say is not None:
            result["开发者说"] = self.dev_say
        if self.danmaku is not None:
            result["弹幕"] = {
                "用户名": self.danmaku.username,
                "内容": self.danmaku.msg
            }
        if self.game_scene is not None:
            result["游戏画面"] = self.game_scene
        if self.game_event is not None:
            result["游戏事件"] = self.game_event.message

        return json.dumps(result)

    def is_meaningful(self) -> bool:
        return not (self.game_event is None and is_blank(self.game_scene) and is_blank(
            self.dev_say) and self.danmaku is None)
