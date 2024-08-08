import yaml

from common.utils.file_util import spath


class AutoConfigLoader:
    config: dict

    def __init__(self):
        pass

    @staticmethod
    def load_config():
        with open(file=spath("config/auto_config.yaml"), mode='r', encoding='utf-8') as f:
            AutoConfigLoader.config = yaml.safe_load(f)
            assert AutoConfigLoader.config is not None, f"自动配置加载失败"


AutoConfigLoader.load_config()
