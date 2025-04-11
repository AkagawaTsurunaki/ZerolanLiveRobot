import os
from pathlib import Path

import yaml
from loguru import logger
from typeguard import typechecked

from config import ZerolanLiveRobotConfig
from common.generator.config_gen import ConfigFileGenerator


@typechecked
def generate_config_file(config_path: Path):
    res_dir = config_path.parent
    if not os.path.exists(res_dir):
        res_dir.mkdir()
    gen = ConfigFileGenerator()
    config = gen.generate_yaml(ZerolanLiveRobotConfig())
    with open(config_path, mode="w+", encoding="utf-8") as f:
        f.write(config)
    logger.warning(
        "`resources/config.yaml` was not found. I have generated the file for you! \n"
        "Please edit the config file and re-run the program.")
    exit()


@typechecked
def get_project_dir() -> Path:
    project_dir = os.getcwd()
    # Suppose we have in the `ZerolanLiveRobot/tests` directory!
    if project_dir.endswith("tests"):
        project_dir = Path(os.getcwd()).parent
    return project_dir


@typechecked
def get_default_config_path() -> Path:
    project_dir = get_project_dir()
    config_file_path = project_dir.joinpath("resources/config.yaml")
    return config_file_path


@typechecked
def get_config(path: Path | None = None) -> ZerolanLiveRobotConfig:
    if path is None:
        path = get_default_config_path()
    if os.path.exists(path):
        with open(path, mode="r", encoding="utf-8") as f:
            cfg_dict = yaml.safe_load(f)
            config = ZerolanLiveRobotConfig.model_validate(cfg_dict)
            return config
    else:
        generate_config_file()
