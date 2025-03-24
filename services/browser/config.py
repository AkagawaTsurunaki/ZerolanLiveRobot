from typing import Literal

from pydantic import BaseModel, Field


class BrowserConfig(BaseModel):
    enable: bool = Field(default=True, description="Enable selenium to controller your browser?\n"
                                                   "Warning: VLA may control your mouse cursor and use keyboards!")
    profile_dir: str | None = Field(default=None,
                                    description="Browser's Profile folder. \n"
                                                "This is to ensure that under Selenium's control, \n"
                                                "your account login and other information will not be lost. If the value is 'null', \n"
                                                "the program will automatically detect the location (Windows only).")
    driver: Literal["chrome", "firefox"] = Field(default="firefox",
                                                 description="Browser drivers, for Selenium. Only Firefox is supported.")
