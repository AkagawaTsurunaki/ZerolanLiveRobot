import asyncio
import inspect
from typing import Dict, List, Callable, Coroutine, Set

from loguru import logger

from common.enumerator import EventEnum


class EventEmitter:
    def __init__(self):
        self.listeners: Dict[str, List[Callable]] = {}
        self.once_listeners: Dict[str, List[Callable]] = {}

    def add_listener(self, event: str, listener, once: bool = False):
        listeners = self.once_listeners if once else self.listeners
        if listeners.get(event) is None:
            listeners[event] = []
        listeners[event].append(listener)
        logger.debug(f"Current listeners {len(listeners[event])}")

    def on(self, event: EventEnum) -> Callable:
        def decorator(func: Coroutine):
            self.add_listener(event.name, func, False)
            return func

        return decorator

    def once(self, event: EventEnum) -> Callable:
        def decorator(func: Coroutine):
            self.add_listener(event.name, func, True)
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

    async def _handle_tasks(self, listeners: list[Callable], once: bool, *args, **kwargs):
        tasks = []
        if listeners is None:
            return
        for listener in listeners:
            if inspect.iscoroutinefunction(listener):
                task = asyncio.create_task(self._handle_async_task(listener(*args, **kwargs)))
                tasks.append(task)
                if once:
                    listeners.remove(listener)
            else:
                self._handle_sync_task(listener(*args, **kwargs))
        await asyncio.gather(*tasks)

    async def emit(self, event: EventEnum, *args, **kwargs) -> None:
        listeners = self.listeners.get(event.name, None)
        once_listeners = self.once_listeners.get(event.name, None)

        # If no listeners to handle error, crashed
        # if listeners is None:
        #     if event == EventEnum.SYSTEM_ERROR:
        #         await emitter.emit(EventEnum.SYSTEM_CRASHED, args)
        #     return

        tasks = [self._handle_tasks(listeners, False, *args, **kwargs),
                 self._handle_tasks(once_listeners, True, *args, **kwargs)]

        await asyncio.gather(*tasks)
        logger.debug(f"Event {event.name} emitted")

    def stop(self):
        self.listeners.clear()


emitter = EventEmitter()
