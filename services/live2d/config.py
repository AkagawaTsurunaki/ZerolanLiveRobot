from pydantic import BaseModel, Field


class Live2DViewerConfig(BaseModel):
    enable: bool = Field(default=True,
                         description="Enable Live2d Viewer?")
    model3_json_file: str = Field(default="./resources/static/models/live2d", description="Path of `xxx.model3.json`")
    auto_lip_sync: bool = Field(default=True, description="Auto lip sync.")
    auto_blink: bool = Field(default=True, description="Auto eye blink.")
    auto_breath: bool = Field(default=True, description="Audio eye blink.")
    win_height: int = Field(default=True, description="Window height.")
    win_width: int = Field(default=True, description="Window width.")
