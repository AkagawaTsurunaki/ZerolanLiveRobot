from pydantic import BaseModel, Field

from common.utils.i18n_util import i18n_config
from services.browser.config import BrowserConfig
from services.game.config import GameBridgeConfig
from services.live2d.config import Live2DViewerConfig
from services.live_stream.config import LiveStreamConfig
from services.obs.config import ObsStudioClientConfig
from services.playground.config import PlaygroundBridgeConfig
from services.playground.res.config import ResourceServerConfig
from services.qqbot.config import QQBotBridgeConfig

_ = i18n_config()


class ServiceConfig(BaseModel):
    res_server: ResourceServerConfig = Field(default=ResourceServerConfig(),
                                             description=_("Configuration for the Resource Server."))
    live_stream: LiveStreamConfig = Field(default=LiveStreamConfig(),
                                          description=_("Configuration for the Live Stream service."))
    game: GameBridgeConfig = Field(default=GameBridgeConfig(),
                                   description=_("Configuration for the Game Bridge service."))
    playground: PlaygroundBridgeConfig = Field(default=PlaygroundBridgeConfig(),
                                               description=_("Configuration for the Playground Bridge service."))
    qqbot: QQBotBridgeConfig = Field(default=QQBotBridgeConfig(),
                                     description=_("Configuration for the QQBot Bridge service."))
    obs: ObsStudioClientConfig = Field(default=ObsStudioClientConfig(),
                                       description=_("Configuration for the OBS Studio Client."))
    browser: BrowserConfig = Field(default=BrowserConfig(), description=_("Browser config."))
    live2d_viewer: Live2DViewerConfig = Field(default=Live2DViewerConfig(),
                                              description=_("Configuration for the Live2DViewer service. "
                                                            "[!Attention]\n"
                                                            "1. When use OBS to capture the window, you should use GameSource. "
                                                            "Then enable `SLI/Cross` and `Allow window transparent` options."
                                                            "Or the windows will not display.\n"
                                                            "2. Use `Window capture` will leave black ground."))
