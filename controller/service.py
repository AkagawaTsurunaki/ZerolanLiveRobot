import json

from flask import Flask

app = Flask(__name__)

DEBUG = False
HOST = '127.0.0.1'
PORT = 11451
CUSTOM_PROMPT_PATH: str = './template/custom_prompt.json'


@app.route('/reset', methods=['GET'])
def reset():
    load_custom_history()
    return '记忆已被重置'


def load_custom_history():
    print(CUSTOM_PROMPT_PATH)
    with open(file=CUSTOM_PROMPT_PATH, mode='r', encoding='utf-8') as file:
        json_value: dict = json.load(file)
        history = json_value.get('history')
        return history


def init(debug: bool, host: str, port: int, custom_prompt_path: str):
    global HOST, DEBUG, PORT, CUSTOM_PROMPT_PATH
    DEBUG = debug
    HOST = host
    PORT = port
    CUSTOM_PROMPT_PATH = custom_prompt_path
    return True


def start():
    app.run(host=HOST, port=PORT, debug=DEBUG)
