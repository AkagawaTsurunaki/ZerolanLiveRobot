import copy
from dataclasses import dataclass
from typing import List

from flask import Flask, request
from loguru import logger

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


# Global variable for shared state
_game_event_list: List[GameEvent] = []


def handle_add_event():
    try:
        game_event = GameEvent(**request.json)
        if game_event:
            _game_event_list.append(game_event)
            logger.info(f'Game Event: {request.json}')
            return 'OK.'
    except Exception as e:
        logger.exception(e)
        return "Failed to add event."


@app.route('/minecraft/addevent', methods=['POST'])
def add_event_route():
    return handle_add_event()


def mark_last_event_as_read_and_clear_list():
    if _game_event_list and len(_game_event_list) > 0:
        ret = copy.deepcopy(_game_event_list[-1])
        _game_event_list.clear()
        return ret
    return None


def select_last_unread_event():
    if _game_event_list:
        unread_event_list = [event for event in _game_event_list if not event.read]
        if unread_event_list and len(unread_event_list) > 0:
            ret = unread_event_list[-1]
            ret.read = True
            return ret
    return None


def start(cfg: GlobalConfig):
    app.run(host=cfg.minecraft.host, port=cfg.minecraft.port, debug=cfg.minecraft.debug)
