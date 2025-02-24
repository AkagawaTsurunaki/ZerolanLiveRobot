import os

from flask import Flask, send_from_directory, jsonify
from flask.logging import create_logger

app = Flask(__name__)
log = create_logger(app)

# 配置默认的音频文件目录
tmp_dir = R'.temp'  # 默认目录，你可以根据需要修改
audio_dir = os.path.join(tmp_dir, "audio")


@app.route('/file/audio/<path:file_name>')
def get_audio_file(file_name):
    """
    提供音频文件下载
    :param file_name: 音频文件名称
    :return: 音频文件或 JSON 错误信息
    """
    try:
        # 检查音频文件是否存在
        file_path = os.path.join(audio_dir, file_name)
        if not os.path.exists(file_path):
            log.error(f"文件 {file_name} 不存在或不可访问。")
            return jsonify({"success": False, "message": f"文件 {file_name} 不存在或不可访问。"})

        # 返回文件
        return send_from_directory(audio_dir, file_name)
    except Exception as e:
        log.error(f"获取文件 {file_name} 时发生错误: {e}")
        return jsonify({"success": False, "message": f"获取文件时发生错误: {e}"}), 500


if __name__ == '__main__':
    # 启动 Flask 应用
    app.run(host='0.0.0.0', port=5000)
