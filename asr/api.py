import requests

import initzr
from utils.datacls import HTTPResponseBody

URL = initzr.load_asr_config().url()


def predict(wav_file_path: str):
    response = requests.get(url=f'{URL}/asr/predict', json={"wav_path": wav_file_path})
    response = HTTPResponseBody(**response.json())
    if response.ok:
        transcript = response.data.get('transcript', None)
        return transcript
    return None