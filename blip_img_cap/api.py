import requests
from utils.datacls import HTTPResponseBody


def inference(img_path: str, prompt: str):
    data = {
        'img_path': img_path,
        'prompt': prompt
    }
    response = requests.get(url='http://127.0.0.1:5926/blip/infer', json=data)
    response = HTTPResponseBody(**response.json())
    assert response.ok
    caption = response.data.get('caption', None)
    return caption
