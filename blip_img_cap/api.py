import requests

import initzr
from utils.datacls import HTTPResponseBody

URL = initzr.load_blip_image_captioning_large_config().url()


def inference(img_path: str, prompt: str):
    data = {
        'img_path': img_path,
        'prompt': prompt
    }
    response = requests.get(url=f'{URL}/blip/infer', json=data)
    response = HTTPResponseBody(**response.json())
    assert response.ok
    caption = response.data.get('caption', None)
    return caption
