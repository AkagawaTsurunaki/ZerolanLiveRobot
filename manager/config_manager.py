import os
from pathlib import Path

import yaml
from typeguard import typechecked

from common.config import ZerolanLiveRobotConfig


#
#
# class ConfigManager:
#
#     def __init__(self):
#         self._config_path = os.path.abspath('resources/config.yaml').replace('\\', '/')
#         self._observer: Observer = None
#         self._modified = 0
#         self._config: ZerolanLiveRobotConfig | None = None
#
#         self.init()
#
#     def init(self):
#         self._load_config()
#         self._register_watchdog()
#
#     def start(self):
#         self._observer.start()
#
#     def join(self):
#         self._observer.join()
#
#     def stop(self):
#         self._observer.stop()
#
#     @property
#     def config(self):
#         return self._config
#
#     def generate_config_file(self):
#         res_dir = Path(self._config_path).parent
#         if not os.path.exists(res_dir):
#             res_dir.mkdir()
#         gen = ConfigFileGenerator()
#         config = gen.generate_yaml(ZerolanLiveRobotConfig())
#         with open(self._config_path, mode="w+", encoding="utf-8") as f:
#             f.write(config)
#         logger.warning(
#             "`resources/config.yaml` was not found. I have generated the file for you! \n"
#             "Please edit the config file and re-run the program.")
#         exit()
#
#     @log_run_time()
#     def _load_config(self):
#         # Check if the config file exists
#         if not os.path.exists(self._config_path):
#             self.generate_config_file()
#         logger.info(f"Loading config file: {self._config_path}")
#         try:
#             cfg_dict = read_yaml(self._config_path)
#             config = ZerolanLiveRobotConfig.model_validate(cfg_dict)
#
#             if self._config is not None and config.model_dump_json() == self._config.model_dump_json():
#                 logger.debug("Config file was modified, but there is no need to update config.")
#                 return
#
#             self._config = config
#             if self._modified > 0:
#                 emitter.emit(ConfigFileModifiedEvent())
#                 logger.info("Config file was modified. Hot reload triggered.")
#             self._modified += 1
#         except Exception as e:
#             # When the `config.yaml` does not meet the criteria, an exception is thrown.
#             logger.exception(e)
#             logger.error("Please check your config file. Maybe there are some mistakes.")
#         logger.info(f"Loaded config file: {self._config_path}")
#
#     def _register_watchdog(self):
#         class ConfigFileModifiedHandler(FileSystemEventHandler):
#             def __init__(self, path: str, update_config: Callable):
#                 super().__init__()
#                 self.path = path
#                 self.update_config = update_config
#
#             def on_modified(self, event):
#                 if not event.is_directory:
#                     src_path = os.path.abspath(str(event.src_path)).replace('\\', '/')
#                     if src_path == self.path:
#                         self.update_config()
#
#         event_handler = ConfigFileModifiedHandler(self._config_path, self._load_config)
#         self._observer = Observer()
#         self._observer.schedule(event_handler, path='.', recursive=True)
#
#
# _config_manager = None

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
        raise FileNotFoundError(f"No such config file: {path}")
