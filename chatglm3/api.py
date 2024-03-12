import asyncio
import json
from dataclasses import asdict
from urllib.parse import urljoin

import requests

from chatglm3.service import SERVICE_URL, LLMQuery, ModelResponse


async def stream_predict(query, history, temperature, top_p):
    llm_query = LLMQuery(query=query, history=history, temperature=temperature, top_p=top_p)
    llm_query = asdict(llm_query)
    response = requests.post(url=urljoin(SERVICE_URL, '/streampredict'), stream=True,
                             json=llm_query)

    for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
        json_val = json.loads(chunk)
        model_resp = ModelResponse(**json_val)
        yield model_resp


async def func():
    async for model_resp in stream_predict(query='test', history=[], temperature=1., top_p=1.):
        print(model_resp.response)


if __name__ == '__main__':
    asyncio.run(func())
