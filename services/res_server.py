import os
from urllib.parse import urljoin

from flask import Flask, abort, send_file
from loguru import logger

from common.abs_runnable import ThreadRunnable
from common.utils.file_util import get_temp_data_dir
from common.utils.web_util import get_local_ip

# 定义资源类型
RESOURCE_TYPES = {
    "audio": "audio",
    "image": "image",
    "video": "video",
    "model": "model",
}


class ResourceServer(ThreadRunnable):
    def name(self):
        return "ResourceServer"

    def stop(self):
        super().stop()

    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.ipv6 = True
        self.local_ip = get_local_ip(self.ipv6)
        self.app = Flask(__name__)
        self.init()

    def init(self):
        @self.app.route('/resource/temp/<resource_type>/<filename>')
        def serve_resource(resource_type: str, filename):
            """
            根据请求的资源类型和文件名，从指定文件夹中提供文件。
            """
            # 检查资源类型是否有效
            if resource_type not in RESOURCE_TYPES:
                abort(404, description="Invalid resource type")

            # 构造文件路径
            file_path = str(os.path.join(resource_type, filename))
            file_path = os.path.join(get_temp_data_dir(), file_path)

            # 检查文件是否存在
            if not os.path.exists(file_path):
                abort(404, description="File not found")

            return send_file(file_path)

    def start(self):
        super().start()
        self.app.run(host=self.host, port=self.port, debug=True, use_reloader=False)

    def path_to_url(self, path: str) -> str:
        path = os.path.abspath(path).replace("\\", "/")
        filename, res_dir = path.split("/")[-1], path.split("/")[-2]
        url = urljoin(f"http://{self.local_ip}:11000", f"/resource/temp/{res_dir}/{filename}")
        logger.debug(f"Convert to url: {url}")
        return url
