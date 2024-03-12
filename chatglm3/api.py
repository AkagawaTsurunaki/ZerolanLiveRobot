import json
from dataclasses import asdict
from http import HTTPStatus
from urllib.parse import urljoin

import requests

from chatglm3.service import SERVICE_URL, LLMQuery, LLMResponse


async def stream_predict(query, history=None, temperature=1., top_p=1.):
    llm_query = LLMQuery(query=query, history=history, temperature=temperature, top_p=top_p)
    llm_query = asdict(llm_query)
    response = requests.post(url=urljoin(SERVICE_URL, '/streampredict'), stream=True,
                             json=llm_query)

    for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
        json_val = json.loads(chunk)
        model_resp = LLMResponse(**json_val)
        yield model_resp.response, model_resp.history


def predict(query, history=None, temperature=1., top_p=1.):
    llm_query = LLMQuery(query=query, history=history, temperature=temperature, top_p=top_p)
    llm_query = asdict(llm_query)
    response = requests.post(url=urljoin(SERVICE_URL, '/predict'), stream=True, json=llm_query)
    if response.status_code == HTTPStatus.OK:
        json_val = response.json()
        llm_resp = LLMResponse(**json_val)

        return llm_resp.response, llm_resp.history
