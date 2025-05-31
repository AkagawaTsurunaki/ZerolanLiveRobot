from pydantic import BaseModel, Field

from common.enumerator import BaseEnum
from common.utils.enum_util import enum_to_markdown
from common.utils.i18n_util import i18n_config

_ = i18n_config()


class DisplayModeEnum(BaseEnum):
    AR: str = "ar"
    Live2D: str = "live2D"


class PlaygroundBridgeConfig(BaseModel):
    enable: bool = Field(default=True,
                         description=_("Whether to enable PlaygroundBridge WebSocket server."))
    host: str = Field(default="0.0.0.0",
                      description=_("The host address of the PlaygroundBridge server."))
    port: int = Field(default=11013,
                      description=_("The port number of the PlaygroundBridge server."))
    mode: DisplayModeEnum = Field(default=DisplayModeEnum.Live2D,
                                  description=_(f"The display mode of the client. {enum_to_markdown(DisplayModeEnum)}"))
    bot_id: str = Field(default=f"<BOT_ID>",
                        description=_("The ID of the bot. \n"
                                      "You can set it to any value."))
    model_dir: str = Field(default="./resources/static/models/live2d/<YOUR_LIVE2D_DIR>",
                           description=_("The path to the model directory."))
