from pydantic import BaseModel, Field

from services.browser.config import BrowserConfig
from services.game.config import GameBridgeConfig
from services.live_stream.config import LiveStreamConfig
from services.obs.config import ObsStudioClientConfig
from services.playground.config import PlaygroundBridgeConfig
from services.qqbot.config import QQBotBridgeConfig
from services.res.config import ResourceServerConfig


class ServiceConfig(BaseModel):
    res_server: ResourceServerConfig = Field(default=ResourceServerConfig(),
                                             description="Configuration for the Resource Server.")
    live_stream: LiveStreamConfig = Field(default=LiveStreamConfig(),
                                          description="Configuration for the Live Stream service.")
    game: GameBridgeConfig = Field(default=GameBridgeConfig(), description="Configuration for the Game Bridge service.")
    playground: PlaygroundBridgeConfig = Field(default=PlaygroundBridgeConfig(),
                                               description="Configuration for the Playground Bridge service.")
    qqbot: QQBotBridgeConfig = Field(default=QQBotBridgeConfig(),
                                     description="Configuration for the QQBot Bridge service.")
    obs: ObsStudioClientConfig = Field(default=ObsStudioClientConfig(),
                                       description="Configuration for the OBS Studio Client.")
    browser: BrowserConfig = Field(default=BrowserConfig(), description="Browser config.")