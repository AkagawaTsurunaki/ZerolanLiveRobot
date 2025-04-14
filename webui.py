from manager.config_manager import get_config
from common.generator.gradio_gen import DynamicConfigPage


def _start_config_webui():
    config = get_config()
    page = DynamicConfigPage(config)
    page.launch()


if __name__ == '__main__':
    _start_config_webui()
