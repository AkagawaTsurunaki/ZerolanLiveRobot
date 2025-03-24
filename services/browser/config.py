from typing import Literal

from pydantic import BaseModel, Field


class BrowserConfig(BaseModel):
    enable: bool = Field(default=True, description="Enable selenium to controller your browser?\n"
                                                   "Warning: VLA may control your mouse cursor and use keyboards!")
    profile_dir: str | None = Field(default=None,
                                    description="Profile dir for your browser. \n"
                                                "Auto find the location of the Firefox profile file in user directory if you set it `null`.")
    driver: Literal["chrome", "firefox"] = Field(default="firefox", description="Only Firefox is supported.")
