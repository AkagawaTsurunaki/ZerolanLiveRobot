from typing import List

from flask import Flask, jsonify
from flask import request
from loguru import logger

from minecraft.common import GameEvent

app = Flask(__name__)

game_event_list: List[GameEvent] = []


@app.route('/addevent', methods=['POST'])
def handle_add_event():
    game_event = GameEvent(**request.json)
    if game_event:
        game_event_list.append(game_event)
    return jsonify(game_event)


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
