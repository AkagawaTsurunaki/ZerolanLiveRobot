from loguru import logger

from common.decorator import playsound
from common.register.sound_register import SoundRegister


class UnsafeOperationException(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)

    @playsound(SoundRegister.error)
    def toast(self, msg):
        logger.error("🛡️ 安全策略阻止此操作\n" + msg, block=True)
