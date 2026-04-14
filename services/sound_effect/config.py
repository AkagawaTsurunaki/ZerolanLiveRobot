from pydantic import BaseModel, Field


class SoundEffectConfig(BaseModel):
    enable: bool = Field(False, description="Whether to enable the SoundEffectService.")
    sound_effect_dir: str = Field("resources/static/sounds/effect",
                                  description="Directory of the sound effect files.\n"
                                              "Supported formats: `.mp3`, `.wav`, `.ogg`, `.m4a`, `.flac`")
