import asyncio
import inspect
from typing import Dict, List, Callable, Coroutine

from loguru import logger


class EventEmitter:
    def __init__(self):
        self.listeners: Dict[str, List[Callable]] = {}

    def add_listener(self, event, listener):
        if self.listeners.get(event) is None:
            self.listeners[event] = []
        self.listeners[event].append(listener)
        logger.debug(f"Current listeners {len(self.listeners[event])}")

    def on(self, event: str) -> Callable:
        def decorator(func: Coroutine):
            self.add_listener(event, func)
            return func

        return decorator

    async def emit(self, event: str, *args, **kwargs) -> None:
        listeners = self.listeners.get(event, None)
        if listeners is None:
            return
        tasks = []
        for listener in listeners:
            try:
                if inspect.iscoroutinefunction(listener):
                    task = asyncio.create_task(listener(*args, **kwargs))
                    tasks.append(task)
                    # await listener(*args, **kwargs)
                else:
                    listener(*args, **kwargs)
            except Exception as e:
                logger.exception(e)
        await asyncio.gather(*tasks)
        logger.debug(f"Event {event} emitted")
