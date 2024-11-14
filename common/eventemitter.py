import asyncio
import inspect
from typing import Dict, List, Callable, Coroutine, Literal

from loguru import logger

_T = Literal[
    "service.live_stream.disconnected",
    "service.live_stream.danmaku",
    "service.live_stream.gift",
    "service.live_stream.super_chat",
    "service.vad.speech_chunk",
    "pipeline.asr",
    "pipeline.llm",
    "pipeline.tts",
    "service.game.login",
    "service.game.chat",
    "error",
    "crashed"
]


class EventEmitter:
    def __init__(self):
        self.listeners: Dict[str, List[Callable]] = {}

    def add_listener(self, event, listener):
        if self.listeners.get(event) is None:
            self.listeners[event] = []
        self.listeners[event].append(listener)
        logger.debug(f"Current listeners {len(self.listeners[event])}")

    def on(self, event: _T) -> Callable:
        # assert event in _T, f"{event} not in {_T}"
        def decorator(func: Coroutine):
            self.add_listener(event, func)
            return func

        return decorator

    def _handle_sync_task(self, task, *args, **kwargs):
        try:
            task(*args, **kwargs)
        except Exception as e:
            asyncio.gather(self.emit("error", e))

    async def _handle_async_task(self, task):
        try:
            await task
        except Exception as e:
            await self.emit("error", e)

    async def emit(self, event: _T, *args, **kwargs) -> None:
        listeners = self.listeners.get(event, None)
        if listeners is None:
            if event == "error":
                await emitter.emit("crashed", args)
            return
        tasks = []
        for listener in listeners:
            if inspect.iscoroutinefunction(listener):
                task = asyncio.create_task(self._handle_async_task(listener(*args, **kwargs)))
                tasks.append(task)
            else:
                self._handle_sync_task(listener(*args, **kwargs))

        await asyncio.gather(*tasks)
        logger.debug(f"Event {event} emitted")


emitter = EventEmitter()
