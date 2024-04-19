import copy
from dataclasses import dataclass, asdict
from typing import List, Final

from flask import Flask, jsonify
from flask import request
from loguru import logger

from utils.datacls import HTTPResponseBody


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


app = Flask(__name__)

game_event_list: List[GameEvent] = []

TIME_WINDOW_SIZE: Final[int] = 2


@app.route('/minecraft/addevent', methods=['POST'])
def handle_add_event():
    try:
        game_event = GameEvent(**request.json)
        if game_event:
            # if game_event_list:
            #     if game_event_list[-1].same_type(game_event):
            #         response = HTTPResponseBody(ok=True, msg='该事件已被合并')
            #         return jsonify(asdict(response))
            game_event_list.append(game_event)
            logger.info(f'Game Event: {request.json}')
            return 'OK.'
    except Exception as e:
        logger.exception(e)
        return "Failed to add event."


def select01():
    if game_event_list and len(game_event_list) > 0:
        ret = copy.deepcopy(game_event_list[-1])
        game_event_list.clear()
        return ret

    return None


def select02():
    if game_event_list:
        unread_event_list = [event for event in game_event_list if not event.read]
        if unread_event_list and len(unread_event_list) > 0:
            ret = unread_event_list[-1]
            ret.read = True
            return ret
    return None


def start():
    app.run(host='127.0.0.1', port=12546, debug=False)
