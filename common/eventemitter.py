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
        listeners = self.listeners[event]
        for listener in listeners:
            if inspect.iscoroutinefunction(listener):
                await listener(*args, **kwargs)
            else:
                listener(*args, **kwargs)

        logger.debug(f"Event {event} emitted")
