from pydantic import BaseModel, Field

from common.utils.i18n_util import i18n_config

_ = i18n_config()


class QQBotBridgeConfig(BaseModel):
    enable: bool = Field(True, description=_("Whether to enable the QQBotBridge."))
    host: str = Field("0.0.0.0", description=_("The host address of the QQBotBridge service."))
    port: int = Field(11014, description=_("The port number of the QQBotBridge service."))
