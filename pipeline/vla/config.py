from pydantic import BaseModel, Field

from common.enumerator import BaseEnum
from common.utils.i18n_util import i18n_config
from pipeline.vla.showui.config import ShowUIConfig

_ = i18n_config()


class VLAModelIdEnum(BaseEnum):
    ShowUI: str = "howlab/ShowUI-2B"


class VLAPipelineConfig(BaseModel):
    showui: ShowUIConfig = Field(default=ShowUIConfig(), description=_("Configuration for the ShowUI component."))
    enable: bool = Field(default=True, description=_("Whether the Visual Language Action pipeline is enabled."))
