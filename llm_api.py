from flask import Flask

from llm.server import handle_config

app = Flask(__name__)

if __name__ == '__main__':
    config = handle_config()
    app.run(config.host, config.port, config.debug)
