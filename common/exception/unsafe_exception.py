from loguru import logger


class UnsafeOperationException(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)

    def toast(self, msg):
        logger.error("🛡️ 安全策略阻止此操作\n" + msg, block=True)
