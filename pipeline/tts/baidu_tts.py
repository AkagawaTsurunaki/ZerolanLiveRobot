import uuid

import requests
from loguru import logger
from pydantic import BaseModel
from zerolan.data.pipeline.tts import TTSPrediction, TTSQuery


def _aue_to_str(aue: int) -> str:
    format_map = {
        3: "mp3",
        4: "pcm",
        5: "pcm",
        6: "wav"
    }

    if aue not in format_map:
        raise ValueError(f"Invalid aue value: {aue}")

    result = format_map[aue]
    return result


def _str_to_aue(type: str):
    format_map = {
        "mp3": 3,
        "pcm": 5,
        "wav": 6
    }

    if type not in format_map:
        raise ValueError(f"Invalid aue value: {type}")

    result = format_map[type]
    return result


class BaiduTTSError(BaseModel):
    """Pydantic model to represent TTS API error response"""
    convert_offline: bool
    err_detail: str
    err_msg: str
    err_no: int
    err_subcode: int
    tts_logid: int


class BaiduTTSPipeline:
    def __init__(self, api_key, secret_key):
        self._access_token = self._get_access_token(api_key, secret_key)
        self._cuid = str(uuid.uuid4())

    @staticmethod
    def _get_access_token(api_key, secret_key):
        """
        使用 AK，SK 生成鉴权签名（Access Token）
        :return: access_token，或是None(如果错误)
        """
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {"grant_type": "client_credentials", "client_id": api_key, "client_secret": secret_key}
        return str(requests.post(url, params=params).json().get("access_token"))

    def predict(self, query: TTSQuery):
        url = "https://tsn.baidu.com/text2audio"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': '*/*'
        }
        if self._access_token is None:
            raise ValueError("Access token should not be None.")
        aue = _str_to_aue(query.audio_type)
        payload = {
            'tex': query.text,
            'tok': self._access_token,
            "cuid": self._cuid,
            "ctp": 1,
            "lan": "zh", # Baidu TTS is not supported `auto`
            "spd": 5,
            "pit": 5,
            "vol": 5,
            "per": 1,
            "aue": aue
        }
        response = requests.request("POST", url, headers=headers, data=payload)

        response.raise_for_status()

        # Get Content-Type header
        content_type = response.headers.get('Content-Type', '').lower()

        # Validate response based on Content-Type
        if content_type.startswith('application/json') or content_type.startswith('text/'):
            # Response is text/JSON - likely an error
            error_data = response.json()
            error = BaiduTTSError(**error_data)
            logger.error(f"Error message received: {error_data}")
            raise Exception(error)
        elif content_type.startswith('audio/') or 'audio' in content_type:
            # Response is audio data - proceed normally
            prediction = TTSPrediction(wave_data=response.content, audio_type=_aue_to_str(aue))
            return prediction
        else:
            raise ValueError(f"Unsupported content type: {content_type}")

    def stream_predict(self, *args, **kwargs):
        raise NotImplementedError("Baidu stream TTS is not supported.")