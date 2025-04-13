from pydantic import BaseModel, Field

from common.enumerator import BaseEnum
from pipeline.vla.showui.config import ShowUIConfig


class VLAModelIdEnum(BaseEnum):
    ShowUI: str = "howlab/ShowUI-2B"


class VLAPipelineConfig(BaseModel):
    showui: ShowUIConfig = Field(default=ShowUIConfig(), description="Configuration for the ShowUI component.")
    enable: bool = Field(default=True, description="Whether the Visual Language Action pipeline is enabled.")
