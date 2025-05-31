from pydantic import BaseModel, Field

from common.utils.i18n_util import i18n_config

_ = i18n_config()


class Live2DViewerConfig(BaseModel):
    enable: bool = Field(default=True,
                         description=_("Enable Live2d Viewer?"))
    model3_json_file: str = Field(default="./resources/static/models/live2d",
                                  description=_("Path of `xxx.model3.json`"))
    auto_lip_sync: bool = Field(default=True, description=_("Auto lip sync."))
    auto_blink: bool = Field(default=True, description=_("Auto eye blink."))
    auto_breath: bool = Field(default=True, description=_("Audio eye blink."))
    win_height: int = Field(default=True, description=_("Window height."))
    win_width: int = Field(default=True, description=_("Window width."))
