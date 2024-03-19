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
    logger.info(game_event)
    if game_event:
        game_event_list.append(game_event)
    return jsonify(game_event)


app.run(host='127.0.0.1', port=12546, debug=False)
