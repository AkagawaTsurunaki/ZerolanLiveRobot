from pydantic import Field

from pipeline.base.base_sync import AbstractPipelineConfig


#######
# VLA #
#######

class ShowUIConfig(AbstractPipelineConfig):
    model_id: str = Field(default="showlab/ShowUI-2B", description="The ID of the model used for the UI.", frozen=True)
    predict_url: str = Field(default="http://127.0.0.1:11000/vla/showui/predict",
                             description="The URL for UI prediction requests.")
    stream_predict_url: str = Field(default="http://127.0.0.1:11000/vla/showui/stream-predict",
                                    description="The URL for streaming UI prediction requests.")
