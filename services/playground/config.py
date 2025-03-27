from typing import Literal

from pydantic import BaseModel, Field


class GRPCServerConfig(BaseModel):
    enable: bool = Field(default=True,
                         description="Whether to enable the gRPC server.\n"
                                     "Note: Must keep enable `true` if PlaygroundBridge is enabled.")
    host: str = Field(default="0.0.0.0",
                      description="The host address of the gRPC server.")
    port: int = Field(default=11020,
                      description="The port number of the gRPC server.")


class PlaygroundBridgeConfig(BaseModel):
    enable: bool = Field(default=True,
                         description="Whether to enable PlaygroundBridge WebSocket server.")
    host: str = Field(default="0.0.0.0",
                      description="The host address of the PlaygroundBridge server.")
    port: int = Field(default=11013,
                      description="The port number of the PlaygroundBridge server.")
    mode: Literal["live2d", "ar"] = Field(default="live2d",
                                          description="The mode type, either `live2d` or `ar`.")
    bot_id: str = Field(default=f"<BOT_ID>",
                        description="The ID of the bot. \n"
                                    "You can set it to any value.")
    model_dir: str = Field(default="./resources/static/models/live2d/<YOUR_LIVE2D_DIR>",
                           description="The path to the model directory.")
    grpc_server: GRPCServerConfig = Field(default=GRPCServerConfig(),
                                          description="The configuration for the gRPC service.")
