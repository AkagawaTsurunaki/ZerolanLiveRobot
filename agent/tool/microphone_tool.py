from typing import Type, Any

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from event.event_data import DeviceMicrophoneSwitchEvent
from event.event_emitter import emitter


class MicrophoneToolInput(BaseModel):
    switch: bool = Field(description="`true` if open the microphone, `false` if close the microphone.")


class MicrophoneTool(BaseTool):
    name: str = "麦克风控制器"
    description: str = "当用户要求打开或关闭麦克风时，使用此工具"
    args_schema: Type[BaseModel] = MicrophoneToolInput
    return_direct: bool = True

    def _run(self, switch: bool) -> Any:
        emitter.emit(DeviceMicrophoneSwitchEvent(switch=switch))
