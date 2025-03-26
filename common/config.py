import os

from loguru import logger
from pydantic import BaseModel, Field

from character.config import CharacterConfig
from common.gen import ConfigFileGenerator
from common.utils.file_util import read_yaml, spath
from services.config import ServiceConfig
from ump.config import PipelineConfig


class ZerolanLiveRobotConfig(BaseModel):
    pipeline: PipelineConfig = Field(default=PipelineConfig(),
                                     description="Configuration for the pipeline settings. \n"
                                                 "The pipeline is the key to connecting to `ZerolanCore`, \n"
                                                 "which typically accesses the model via HTTP or HTTPS requests and gets a response from the model. \n"
                                                 "> [!NOTE] \n"
                                                 "> 1. At a minimum, you need to enable the LLMPipeline. \n"
                                                 "> 2. ZerolanCore is distributed, and you can deploy different models to different servers. Just set different url to connect to your models. \n"
                                                 "> 3. If your server can only open one port, try forwarding your network requests using [Nginx](https://nginx.org/en/).")
    service: ServiceConfig = Field(default=ServiceConfig(),
                                   description="Configuration for the service settings. \n"
                                               "The services are usually opened locally, \n"
                                               "and instances of other projects establish WebSocket or HTTP connections with the service, \n"
                                               "and the service controls the behavior of its sub-project instances.")
    character: CharacterConfig = Field(default=CharacterConfig(),
                                       description="Configuration for the character settings.")

# Check if the config file exists
if not os.path.exists("resources/config.yaml"):
    gen = ConfigFileGenerator()
    config = gen.generate_yaml(ZerolanLiveRobotConfig())
    with open("resources/config.yaml", mode="w+", encoding="utf-8") as f:
        f.write(config)
    logger.warning(
        "`resources/config.yaml` was not found. I have generated the file for you! \n"
        "Please edit the config file and re-run the program.")
    exit()


def get_config() -> ZerolanLiveRobotConfig:
    try:
        cfg_dict = read_yaml(spath("resources/config.yaml"))
    except Exception as e:
        logger.error("Are you sure that you run the program in the proper location? ")
        raise e
    try:
        config = ZerolanLiveRobotConfig.model_validate(cfg_dict)
    except Exception as e:
        # When the `config.yaml` does not meet the criteria, an exception is thrown.
        logger.error("Please check your `config.yaml`. Maybe there are some mistakes.")
        raise e
    return config
