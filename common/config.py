from loguru import logger
from pydantic import BaseModel, Field

from character.config import CharacterConfig
from common.utils.file_util import read_yaml, spath
from ump.config import PipelineConfig
from services.config import ServiceConfig


class ZerolanLiveRobotConfig(BaseModel):
    pipeline: PipelineConfig = Field(default=PipelineConfig(),
                                     description="Configuration for the pipeline settings.")
    service: ServiceConfig = Field(default=ServiceConfig(),
                                   description="Configuration for the service settings.")
    character: CharacterConfig = Field(default=CharacterConfig(),
                                       description="Configuration for the character settings.")


def get_config() -> ZerolanLiveRobotConfig:
    try:
        cfg_dict = read_yaml(spath("resources/config.yaml"))
    except Exception as e:
        logger.error("Are you sure that you have copied `config.yaml` from `config.template.yaml` in `resources`?`")
        raise e
    try:
        config = ZerolanLiveRobotConfig.model_validate(cfg_dict)
    except Exception as e:
        # When the `config.yaml` does not meet the criteria, an exception is thrown.
        logger.error("Please check your `config.yaml`. Maybe there are some mistakes.")
        raise e
    return config
