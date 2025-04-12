from pydantic import BaseModel, Field


class MicrophoneConfig(BaseModel):
    enable: bool = Field(default=True, alias='Enable the microphone in your local machine.')
    threshold: int = Field(default=100, description="Threshold of the speech be detected.")
    max_mute_count: int = Field(default=2, description="Maximum number of mute chunks.")
    pad: int = Field(default=1, description="Padding of detected speech data.")


class DeviceConfig(BaseModel):
    microphone: MicrophoneConfig = Field(default=MicrophoneConfig(), description="Config of the microphone.")
