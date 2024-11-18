import asyncio
import inspect
from typing import Dict, List, Callable, Coroutine

from loguru import logger

from common.enumerator import EventEnum


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
            asyncio.gather(self.emit(EventEnum.SYSTEM_ERROR, e))

    async def _handle_async_task(self, task):
        try:
            await task
        except Exception as e:
            await self.emit(EventEnum.SYSTEM_ERROR, e)

    async def emit(self, event: EventEnum, *args, **kwargs) -> None:
        listeners = self.listeners.get(event.name, None)
        if listeners is None:
            if event == EventEnum.SYSTEM_ERROR:
                await emitter.emit(EventEnum.SYSTEM_CRASHED, args)
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
