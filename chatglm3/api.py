import json
from dataclasses import asdict
from http import HTTPStatus
from urllib.parse import urljoin

import requests

import initzr
from utils.datacls import LLMQuery, LLMResponse

SERVICE_URL = 'http://127.0.0.1:8085'


def init():
    global SERVICE_URL
    config = initzr.load_chatglm3_service_config()
    SERVICE_URL = f'http://{config.host}:{config.port}'


def check_alive():
    try:
        requests.head(SERVICE_URL, timeout=5).status_code
    except Exception as e:
        raise ConnectionError(f'❌️ ChatGLM3 服务无法连接至 {SERVICE_URL}')


async def stream_predict(query, history=None, temperature=1., top_p=1.):
    llm_query = LLMQuery(query=query, history=history, temperature=temperature, top_p=top_p)
    llm_query = asdict(llm_query)
    response = requests.get(url=urljoin(SERVICE_URL, '/chatglm3/streampredict'), stream=True,
                            json=llm_query)

    for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
        json_val = json.loads(chunk)
        model_resp = LLMResponse(**json_val)
        yield model_resp.response, model_resp.history


def predict(query, history=None, temperature=1., top_p=1.):
    llm_query = LLMQuery(query=query, history=history, temperature=temperature, top_p=top_p)
    llm_query = asdict(llm_query)
    response = requests.get(url=urljoin(SERVICE_URL, '/chatglm3/predict'), stream=True, json=llm_query)
    if response.status_code == HTTPStatus.OK:
        json_val = response.json()
        llm_resp = LLMResponse(**json_val)

        return llm_resp.response, llm_resp.history


init()
check_alive()
