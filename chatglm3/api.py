from flask import Flask, request, jsonify
from flask_socketio import SocketIO

import service

app = Flask(__name__)
socketio = SocketIO(app)


@app.route('/predict', methods=['POST'])
def predict():
    query = request.json.get('query')
    history = request.json.get('history', [])
    top_p = float(request.json.get('top_p', 1.))
    temperature = float(request.json.get('temperature', 1.))
    return_past_key_values = request.json.get('return_past_key_values', True)

    def stream_response():
        for chunk in service.stream_predict(query, history, top_p, temperature, return_past_key_values):
            socketio.emit('prediction', {'chunk': chunk}, namespace='/stream')
            # 这里可以根据需要调整发送频率，比如加上延时

    socketio.start_background_task(target=stream_response)
    return jsonify({'message': 'Prediction started.'})


@socketio.on('connect', namespace='/stream')
def stream_connect():
    print('Client connected')


@socketio.on('disconnect', namespace='/stream')
def stream_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app)
