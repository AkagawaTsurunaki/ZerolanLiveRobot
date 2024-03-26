import blip_img_cap.service
from initzr import load_global_config, load_blip_image_captioning_large_config


def start():
    g_config = load_global_config()
    config = load_blip_image_captioning_large_config(g_config)
    assert blip_img_cap.service.init(*config)
    blip_img_cap.service.start()


start()
