from dataclasses import dataclass, asdict
from typing import List, Final

from flask import Flask, jsonify
from flask import request
from loguru import logger

from utils.datacls import HTTPResponseBody


@dataclass
class EventType:
    RILE_EVENT = "RILE_EVENT"
    PROPITIATE = "PROPITIATE"
    RESPAWN = "RESPAWN"
    FARMING = "FARMING"
    FARMED = "FARMED"
    FERTILIZING = "FERTILIZING"
    FERTILIZED = "FERTILIZED"
    HARVESTING = "HARVESTING"
    HARVESTED = "HARVESTED"
    BOT_HURT = "BOT_HURT"


@dataclass
class GameEvent:
    read: bool
    time_stamp: float
    event_type: EventType
    health: int
    food: int
    environment: str

    def aeq(self, other):
        if other:
            if isinstance(other, GameEvent):
                return self.event_type == other.event_type and self.environment == self.environment
        return False


app = Flask(__name__)

game_event_list: List[GameEvent] = []

TIME_WINDOW_SIZE: Final[int] = 2


@app.route('/addevent', methods=['POST'])
def handle_add_event():
    try:
        game_event = GameEvent(**request.json)
        if game_event:
            if game_event_list:
                if game_event_list[-1].aeq(game_event):
                    response = HTTPResponseBody(ok=True, msg='该事件已被合并')
                    return jsonify(asdict(response))
            game_event_list.append(game_event)
            logger.info(request.json)
            response = HTTPResponseBody(ok=True, msg='该事件已被添加', data=asdict(game_event))
            return jsonify(response)
    except Exception as e:
        logger.exception(e)
        response = HTTPResponseBody(ok=False, msg='该事件无法被解析')
        return jsonify(response)


def select01():
    if game_event_list:
        unread_event_list = [event for event in game_event_list if not event.read]
        if unread_event_list and len(unread_event_list) > 0:
            ret = unread_event_list[-1]
            ret.read = True
            return ret
    return None


def start():
    app.run(host='127.0.0.1', port=12546, debug=False)
