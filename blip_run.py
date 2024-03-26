import blip_img_cap.service
from initzr import load_global_config, load_blip_image_captioning_large_config

DEFAULT_GLOBAL_CONFIG_PATH = R'config/global_config.yaml'
g_config = load_global_config(DEFAULT_GLOBAL_CONFIG_PATH)


def start():
    config = load_blip_image_captioning_large_config(g_config)
    assert blip_img_cap.service.init(*config)
    blip_img_cap.service.start()


start()
