import os
import base64
from typing import Generator

from openai import OpenAI
from typeguard import typechecked
from zerolan.data.pipeline.img_cap import ImgCapQuery, ImgCapPrediction

from pipeline.imgcap.config import OpenAIFormatConfig


class OpenAIImgCapPipeline:

    def __init__(self, config: OpenAIFormatConfig):
        """
        Initialize OpenAI-compatible Image Captioning Pipeline.
        :param config: OpenAI format configuration containing api_key, base_url, model, etc.
        """
        self._api_key = config.api_key
        self._base_url = config.base_url
        self._model = config.model
        self._max_tokens = config.max_tokens
        
        # Ensure base_url ends with /v1 for OpenAI compatibility
        if not self._base_url.endswith('/v1'):
            if self._base_url.endswith('/'):
                self._base_url = self._base_url.rstrip('/') + '/v1'
            else:
                self._base_url = self._base_url + '/v1'
        
        self._client = OpenAI(api_key=self._api_key, base_url=self._base_url)

    @typechecked
    def predict(self, query: ImgCapQuery) -> ImgCapPrediction:
        """
        Generate image caption using OpenAI-compatible API.
        :param query: ImgCap query containing image path.
        :return: ImgCap prediction with caption.
        """
        assert os.path.exists(query.img_path), f"{query.img_path} does not exist!"
        assert self._api_key is not None and self._api_key != "", "API key must be provided!"

        # Read and encode image to base64
        with open(query.img_path, 'rb') as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')

        # Prepare messages for vision model
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Describe this image in detail. Provide a clear and comprehensive caption."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]

        # Call OpenAI API
        completion = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            max_tokens=self._max_tokens
        )

        caption = completion.choices[0].message.content
        
        return ImgCapPrediction(caption=caption)

    def stream_predict(self, query: ImgCapQuery, chunk_size: int | None = None) -> Generator[
            ImgCapPrediction, None, None]:
        """
        Stream predict is not directly supported for image captioning.
        We convert it to regular predict.
        :param query: ImgCap query containing image path.
        :param chunk_size: Not used.
        :return: Generator yielding ImgCap prediction.
        """
        yield self.predict(query)
