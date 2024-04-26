import copy
from dataclasses import dataclass
from typing import List

from flask import Flask
from flask import request
from loguru import logger

from common.abs_app import AbstractApp
from config import GlobalConfig

app = Flask(__name__)


@dataclass
class GameEvent:
    read: bool
    health: int
    food: int
    type: str
    description: str

    def same_type(self, other):
        if other and isinstance(other, GameEvent):
            if other.type == self.type:
                return True
        return False


class MinecraftApp(AbstractApp):

    def __init__(self, cfg: GlobalConfig):
        super().__init__()
        self._game_event_list: List[GameEvent] = []
        self.host = cfg.minecraft.host
        self.port = cfg.minecraft.port
        self.debug = cfg.minecraft.debug

    def start(self):
        app.run(host=self.host, port=self.port, debug=self.debug)

    @app.route('/minecraft/addevent', methods=['POST'])
    def handle_add_event(self):
        try:
            game_event = GameEvent(**request.json)
            if game_event:
                self._game_event_list.append(game_event)
                logger.info(f'Game Event: {request.json}')
                return 'OK.'
        except Exception as e:
            logger.exception(e)
            return "Failed to add event."

    def select01(self):
        if self._game_event_list and len(self._game_event_list) > 0:
            ret = copy.deepcopy(self._game_event_list[-1])
            self._game_event_list.clear()
            return ret

        return None

    def select02(self):
        if self._game_event_list:
            unread_event_list = [event for event in self._game_event_list if not event.read]
            if unread_event_list and len(unread_event_list) > 0:
                ret = unread_event_list[-1]
                ret.read = True
                return ret
        return None
