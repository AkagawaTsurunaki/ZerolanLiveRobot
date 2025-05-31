from typing import Literal

from pydantic import BaseModel, Field

from common.enumerator import BaseEnum
from common.utils.enum_util import enum_to_markdown
from common.utils.i18n_util import i18n_config

_ = i18n_config()


class SeleniumDriverEnum(BaseEnum):
    Firefox: str = "Firefox"


class BrowserConfig(BaseModel):
    enable: bool = Field(default=True, description=_("Enable selenium to controller your browser?\n"
                                                     "Warning: VLA may control your mouse cursor and use keyboards!"))
    profile_dir: str | None = Field(default=None,
                                    description=_("Browser's Profile folder. \n"
                                                  "This is to ensure that under Selenium's control, \n"
                                                  "your account login and other information will not be lost. If the value is 'null', \n"
                                                  "the program will automatically detect the location (Windows only)."))
    driver: SeleniumDriverEnum = Field(default=SeleniumDriverEnum.Firefox,
                                       description=_("Browser drivers, for Selenium. \n"
                                                     f"{enum_to_markdown(SeleniumDriverEnum)}"))
