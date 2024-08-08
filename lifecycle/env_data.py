import json
from abc import abstractmethod
from dataclasses import dataclass

from common.utils.str_util import is_blank
from services.live_stream.pipeline import Danmaku


@dataclass
class EnvInputData:

    @abstractmethod
    def to_dict(self) -> dict:
        pass

    @abstractmethod
    def is_empty(self) -> bool:
        pass

    @abstractmethod
    def to_json(self) -> str:
        pass


@dataclass
class MinecraftGameEnvInfo:
    health: int
    food: int
    env: str


@dataclass
class MinecraftLiveStreamData(EnvInputData):
    dev_say: str
    danmaku: Danmaku
    game_scn: str
    game_env_info: MinecraftGameEnvInfo | None

    def to_dict(self):
        result = dict()
        if self.dev_say is not None:
            result["开发者说"] = self.dev_say
        if self.danmaku is not None:
            result["弹幕"] = {
                "用户名": self.danmaku.username,
                "内容": self.danmaku.msg
            }
        if self.game_scn is not None:
            result["游戏画面"] = self.game_scn
        if self.game_env_info is not None:
            result["游戏状态"] = {
                "生命值": self.game_env_info.health,
                "食物值": self.game_env_info.food,
                "周围环境": self.game_env_info.env
            }
        return result

    def __str__(self):
        return str(json.dumps(self.to_dict(), ensure_ascii=False))

    def is_empty(self) -> bool:
        return self.game_env_info is None and is_blank(self.game_scn) and is_blank(
            self.dev_say) and self.danmaku is None
