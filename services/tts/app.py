"""
尚未实现
"""
from common.abs_app import AbstractApplication
from loguru import logger


class TTSApplication(AbstractApplication):
    def run(self):
        logger.warning("形式启动")

    def _handle_predict(self):
        raise NotImplementedError("形式路由")

    def _handle_stream_predict(self):
        raise NotImplementedError("形式路由")
