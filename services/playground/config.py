from pydantic import BaseModel, Field

from common.enumerator import BaseEnum
from common.utils.enum_util import enum_to_markdown


class DisplayModeEnum(BaseEnum):
    AR: str = "ar"
    Live2D: str = "live2D"


class PlaygroundBridgeConfig(BaseModel):
    enable: bool = Field(default=True,
                         description="Whether to enable PlaygroundBridge WebSocket server.")
    host: str = Field(default="0.0.0.0",
                      description="The host address of the PlaygroundBridge server.")
    port: int = Field(default=11013,
                      description="The port number of the PlaygroundBridge server.")
    mode: DisplayModeEnum = Field(default=DisplayModeEnum.Live2D,
                                  description=f"The display mode of the client. {enum_to_markdown(DisplayModeEnum)}")
    bot_id: str = Field(default=f"<BOT_ID>",
                        description="The ID of the bot. \n"
                                    "You can set it to any value.")
    model_dir: str = Field(default="./resources/static/models/live2d/<YOUR_LIVE2D_DIR>",
                           description="The path to the model directory.")
