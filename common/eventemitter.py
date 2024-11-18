import asyncio
import inspect
from enum import Enum
from typing import Dict, List, Callable, Coroutine, Union

from loguru import logger


class EventEnum(str, Enum):
    ...


class Event:
    class Pipeline(EventEnum):
        ASR = "pipeline.asr"
        LLM = "pipeline.llm"
        TTS = "pipeline.tts"

    class Service:
        class LiveStream(EventEnum):
            Disconnected = "service.live_stream.disconnected"
            Danmaku = "service.live_stream.danmaku"
            Gift = "service.live_stream.gift"
            SuperChat = "service.live_stream.super_chat"

        class VAD(EventEnum):
            SpeechChunk = "service.vad.speech_chunk"

        class Game(EventEnum):
            Connected = "service.game.connected"
            Disconnected = "service.game.disconnected"

    class System(EventEnum):
        Error = "system.error"
        Crashed = "system.crashed"


class EventEmitter:
    def __init__(self):
        self.listeners: Dict[str, List[Callable]] = {}

    def add_listener(self, event: str, listener):
        if self.listeners.get(event) is None:
            self.listeners[event] = []
        self.listeners[event].append(listener)
        logger.debug(f"Current listeners {len(self.listeners[event])}")

    def on(self, event: EventEnum) -> Callable:
        # assert event in _T, f"{event} not in {_T}"

        def decorator(func: Coroutine):
            self.add_listener(event.name, func)
            return func

        return decorator

    def _handle_sync_task(self, task, *args, **kwargs):
        try:
            task(*args, **kwargs)
        except Exception as e:
            asyncio.gather(self.emit(Event.System.Error, e))

    async def _handle_async_task(self, task):
        try:
            await task
        except Exception as e:
            await self.emit(Event.System.Error, e)

    async def emit(self, event: EventEnum, *args, **kwargs) -> None:
        listeners = self.listeners.get(event.name, None)
        if listeners is None:
            if event == Event.System.Error:
                await emitter.emit(Event.System.Crashed, args)
            return
        tasks = []
        for listener in listeners:
            if inspect.iscoroutinefunction(listener):
                task = asyncio.create_task(self._handle_async_task(listener(*args, **kwargs)))
                tasks.append(task)
            else:
                self._handle_sync_task(listener(*args, **kwargs))

        await asyncio.gather(*tasks)
        logger.debug(f"Event {event.name} emitted")

    def stop(self):
        self.listeners.clear()


emitter = EventEmitter()
