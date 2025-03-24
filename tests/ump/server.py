import json

import flask
from flask import request
from zerolan.data.pipeline.abs_data import AbstractModelPrediction
from zerolan.data.pipeline.llm import LLMPrediction, Conversation, RoleEnum

"""
This server is just for test. But you can learn how to implement your server!
"""


class TestServer:
    def __init__(self):
        self._host = "127.0.0.1"
        self._port = 5889
        self._app = flask.Flask(__name__)

    def start(self):
        print("Starting test server")
        self._app.run(host=self._host, port=self._port)

    def init(self):
        @self._app.route('/llm/predict', methods=['POST'])
        def llm_predict():
            assert len(request.json) > 0
            id = request.json['id']
            prediction = LLMPrediction(id=id, response="Test passed",
                                       history=[Conversation(role=RoleEnum.user, content="Test"),
                                                Conversation(role=RoleEnum.assistant, content="Test passed")])
            return flask.jsonify(prediction.model_dump())

        @self._app.route('/llm/stream-predict', methods=['POST'])
        def llm_stream_predict():
            assert len(request.json) > 0
            id = request.json['id']
            content = "Test passed"

            def gen():
                for i in range(len(content)):
                    prediction = LLMPrediction(id=id, response=content[:i],
                                               history=[Conversation(role=RoleEnum.user, content="Test"),
                                                        Conversation(role=RoleEnum.assistant, content=content[:i])])
                    yield prediction.model_dump_json()

            return flask.Response(gen())

        @self._app.route('/abs-img/predict', methods=['POST'])
        def abs_img_predict():
            if request.headers['Content-Type'] == 'application/json':
                # If it's in JSON format, then there must be an image location.
                json_val = request.get_json()
                id = json_val['id']
                return flask.jsonify(AbstractModelPrediction(id=id).model_dump())
            elif 'multipart/form-data' in request.headers['Content-Type']:
                # If it's in multipart/form-data format, then try to get the image file.
                img = request.files['image']
                assert img is not None
                # Note: you must get json data from `form['json']`!
                query = json.loads(request.form['json'])
                id = query['id']
                return flask.jsonify(AbstractModelPrediction(id=id).model_dump())
            else:
                raise NotImplementedError("Unsupported Content-Type.")

        @self._app.route('/abs-img/stream-predict', methods=['POST'])
        def abs_img_stream_predict():

            def gen(id):
                for i in range(10):
                    prediction = AbstractModelPrediction(id=id)
                    yield prediction.model_dump_json()

            if request.headers['Content-Type'] == 'application/json':
                # If it's in JSON format, then there must be an image location.
                json_val = request.get_json()
                id = json_val['id']
                return flask.Response(gen(id))
            elif 'multipart/form-data' in request.headers['Content-Type']:
                # If it's in multipart/form-data format, then try to get the image file.
                img = request.files['image']
                assert img is not None
                # Note: you must get json data from `form['json']`!
                query = json.loads(request.form['json'])
                id = query['id']
                return flask.Response(gen(id))
            else:
                raise NotImplementedError("Unsupported Content-Type.")


if __name__ == '__main__':
    # To test, start this first
    test_server = TestServer()
    test_server.init()
    test_server.start()
