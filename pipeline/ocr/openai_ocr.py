import os
import base64
from typing import Generator

from openai import OpenAI
from typeguard import typechecked
from zerolan.data.pipeline.ocr import OCRQuery, OCRPrediction, RegionResult, Position, Vector2D

from common.utils.str_util import remove_md_blocks
from pipeline.ocr.config import OpenAIFormatConfig


class OpenAIOCRPipeline:

    def __init__(self, config: OpenAIFormatConfig):
        """
        Initialize OpenAI-compatible OCR Pipeline.
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

        # OpenAI doesn't provide confidence, use default
        # Warning:
        #   This field may affect the behavior of OCR + ImgCap, see `bot.py` for more details.
        #   A better method to calculate the confidence of the results from OCR may be based on ENTROPY?
        self._default_confidence = 0.95

    @typechecked
    def predict(self, query: OCRQuery) -> OCRPrediction:
        """
        Extract text from image using OpenAI-compatible API.
        :param query: OCR query containing image path.
        :return: OCR prediction with extracted text regions.
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
                        "text": "Extract all text from this image. Return the text content in the order it appears, preserving line breaks. If there are multiple text regions, list them separately."
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

        text_content = completion.choices[0].message.content

        # Clean up markdown code blocks if present
        # @AkagawaTsurunaki moved the code snippets to `str_util.py`.
        # All test cases passed
        text_content = remove_md_blocks(text_content)

        # Convert text to OCRPrediction format
        return self._to_pipeline_format(text_content)

    def stream_predict(self, query: OCRQuery, chunk_size: int | None = None) -> Generator[
            OCRPrediction, None, None]:
        """
        Stream predict is not directly supported for OCR.
        We convert it to regular predict.
        :param query: OCR query containing image path.
        :param chunk_size: Not used.
        :return: Generator yielding OCR prediction.
        """
        yield self.predict(query)

    def _to_pipeline_format(self, text_content: str):
        # Since OpenAI doesn't provide bounding boxes, we create a single region result
        region_results = []
        if text_content and text_content.strip():
            # Split by lines and create region results
            lines = text_content.strip().split('\n')
            for idx, line in enumerate(lines):
                if line.strip():
                    region_results.append(RegionResult(
                        content=line.strip(),
                        confidence=self._default_confidence,
                        position=Position(
                            lu=Vector2D(x=0.0, y=float(idx)),
                            ru=Vector2D(x=0.0, y=float(idx)),
                            rd=Vector2D(x=0.0, y=float(idx)),
                            ld=Vector2D(x=0.0, y=float(idx)),
                        )
                    ))
        return OCRPrediction(region_results=region_results)