import os
import base64
from typing import Generator, List

from openai import OpenAI
from typeguard import typechecked
from zerolan.data.pipeline.vid_cap import VidCapQuery, VidCapPrediction

from pipeline.vidcap.config import OpenAIFormatConfig

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False


class OpenAIVidCapPipeline:

    def __init__(self, config: OpenAIFormatConfig):
        """
        Initialize OpenAI-compatible Video Captioning Pipeline.
        :param config: OpenAI format configuration containing api_key, base_url, model, etc.
        """
        self._api_key = config.api_key
        self._base_url = config.base_url
        self._model = config.model
        self._max_tokens = config.max_tokens
        self._frames_per_second = config.frames_per_second
        
        # Ensure base_url ends with /v1 for OpenAI compatibility
        if not self._base_url.endswith('/v1'):
            if self._base_url.endswith('/'):
                self._base_url = self._base_url.rstrip('/') + '/v1'
            else:
                self._base_url = self._base_url + '/v1'
        
        self._client = OpenAI(api_key=self._api_key, base_url=self._base_url)
        
        if not CV2_AVAILABLE:
            raise ImportError("cv2 (OpenCV) is required for video processing. Please install it: pip install opencv-python")

    def _extract_frames(self, video_path: str) -> List[bytes]:
        """
        Extract frames from video at specified rate.
        :param video_path: Path to video file.
        :return: List of frame images as bytes.
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = int(fps / self._frames_per_second) if fps > 0 else 30
        
        frames = []
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_interval == 0:
                # Encode frame as JPEG
                _, buffer = cv2.imencode('.jpg', frame)
                frames.append(buffer.tobytes())
            
            frame_count += 1
        
        cap.release()
        return frames

    @typechecked
    def predict(self, query: VidCapQuery) -> VidCapPrediction:
        """
        Generate video caption using OpenAI-compatible API.
        :param query: VidCap query containing video path.
        :return: VidCap prediction with caption.
        """
        assert os.path.exists(query.vid_path), f"{query.vid_path} does not exist!"
        assert self._api_key is not None and self._api_key != "", "API key must be provided!"

        # Extract frames from video
        frames = self._extract_frames(query.vid_path)
        
        if not frames:
            return VidCapPrediction(caption="No frames extracted from video.")

        # Encode frames to base64
        base64_frames = []
        for frame_bytes in frames:
            base64_frame = base64.b64encode(frame_bytes).decode('utf-8')
            base64_frames.append(base64_frame)

        # Prepare messages for vision model
        content = [
            {
                "type": "text",
                "text": "Describe this video in detail based on the extracted frames. Provide a comprehensive caption that captures the main actions, scenes, and content."
            }
        ]
        
        # Add frames to content (OpenAI API supports multiple images in one message)
        for base64_frame in base64_frames:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_frame}"
                }
            })

        messages = [
            {
                "role": "user",
                "content": content
            }
        ]

        # Call OpenAI API
        completion = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            max_tokens=self._max_tokens
        )

        caption = completion.choices[0].message.content
        
        return VidCapPrediction(caption=caption)

    def stream_predict(self, query: VidCapQuery, chunk_size: int | None = None) -> Generator[
            VidCapPrediction, None, None]:
        """
        Stream predict is not directly supported for video captioning.
        We convert it to regular predict.
        :param query: VidCap query containing video path.
        :param chunk_size: Not used.
        :return: Generator yielding VidCap prediction.
        """
        yield self.predict(query)
