import asyncio
import inspect
import threading
from asyncio import Task
from enum import Enum
from typing import Callable, List, Dict, TypeVar, Coroutine, Any, Tuple
from uuid import uuid4

from deprecated.sphinx import deprecated
from loguru import logger

from common.abs_runnable import AbstractRunnable
from common.enumerator import EventEnum
from common.thread_killer import KillableThread
from event.event_data import BaseEvent


@deprecated(version='2.1',
            reason="EventEmitter has performance issues, it is recommended that you can use TypedEventEmitter instead.")
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
            logger.exception(e)
            asyncio.gather(self.emit(EventEnum.SYSTEM_ERROR, e))

    async def _handle_async_task(self, task):
        try:
            await task
        except Exception as e:
            logger.exception(e)
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
                self._handle_sync_task(listener, *args, **kwargs)
        await asyncio.gather(*tasks)

    async def emit(self, event: EventEnum, *args, **kwargs) -> None:
        listeners = self.listeners.get(event.name, None)
        once_listeners = self.once_listeners.get(event.name, None)

        tasks = [self._handle_tasks(listeners, False, *args, **kwargs),
                 self._handle_tasks(once_listeners, True, *args, **kwargs)]

        await asyncio.gather(*tasks)
        logger.debug(f"Event {event.name} emitted")

    def stop(self):
        self.listeners.clear()


#########################
#  Typed Event Emitter  #
#########################

Event = TypeVar('Event', bound=BaseEvent)


class Listener:
    def __init__(self, func: Callable[[Event], None], once: bool):
        assert isinstance(func, Callable)
        assert isinstance(once, bool)

        self.id: str = str(uuid4())
        self.func: Callable[[BaseEvent], None] = func
        self.once: bool = once
        self.awaitable: bool = False  # Need judge


class TypedEventEmitter(AbstractRunnable):

    def __init__(self):
        super().__init__()
        self._max_listeners: int = 100
        self._cur_listeners: int = 0
        self._stop_flag: bool = False
        self._event_pending = asyncio.Event()
        self._thread_event = threading.Event()
        self._listeners: Dict[str, List[Listener]] = dict()
        self._tasks: List[Task] = []
        self._sync_loop_thread = KillableThread(target=self._sync_loop, daemon=True,
                                                name="TypedEventEmitterSyncEventLoop")
        self._sync_tasks: List[Tuple[Listener, Event]] = []

    async def astart(self):
        await super().astart()
        logger.info("Starting...")
        self._stop_flag = False

        # NOTE: Start thread first, then start async event loop.
        self._sync_loop_thread.start()
        await self._async_loop()

        # Join the thread
        self._sync_loop_thread.join()

        logger.info("TypedEventEmitter exited")

    async def _async_loop(self):
        while not self._stop_flag:
            for task in self._tasks:
                try:
                    await task
                except asyncio.CancelledError:
                    logger.warning(f"Task cancelled: {task.get_name()}")
                    pass
                self._tasks.remove(task)
            self._event_pending.clear()
            if self._stop_flag:
                break
            await self._event_pending.wait()

    def _sync_loop(self):
        while not self._stop_flag:
            for listener, event in self._sync_tasks:
                listener.func(event)

            self._thread_event.clear()
            if self._stop_flag:
                break
            self._thread_event.wait()

    def emit(self, event: Event):
        self.activate_check()
        assert isinstance(event, BaseEvent)
        listeners = self._listeners.get(event.type.value, None)
        if listeners is None:
            return
        for listener in listeners:
            if listener.once:
                self._listeners[event.type.value].remove(listener)
            if inspect.iscoroutinefunction(listener.func):
                self._add_async_task(listener, event)
            else:
                self._add_sync_task(listener, event)

    def on(self, event: EventEnum):
        assert isinstance(event, Enum)

        def decorator(func: Callable[[Event], None] | Callable[[Event], Coroutine[Any, Any, None]]):
            assert isinstance(func, Callable)
            self._add_listener(event, Listener(func, False))

        return decorator

    def once(self, event: EventEnum):
        assert isinstance(event, Enum)

        def decorator(func: Callable[[Event], None] | Callable[[Event], Coroutine[Any, Any, None]]):
            assert isinstance(func, Callable)
            self._add_listener(event, Listener(func, True))

        return decorator

    async def astop(self):
        await super().astop()
        self._stop_flag = True
        self._event_pending.set()
        for task in self._tasks:
            task.cancel()
        self._sync_loop_thread.kill()
        logger.info("Stopping...")

    def _add_sync_task(self, listener: Listener, event: Event):
        self._sync_tasks.append((listener, event))
        self._thread_event.set()
        logger.debug(f"Added sync task to event loop: {listener.id}")

    def _add_async_task(self, listener: Listener, event: Event):
        task = asyncio.create_task(listener.func(event), name=listener.id)
        self._tasks.append(task)
        self._event_pending.set()
        logger.debug(f"Added async task to event loop: {task.get_name()}")

    def _add_listener(self, event: EventEnum, listener: Listener):
        listeners = self._listeners.get(event.value, None)
        if listeners is None:
            self._listeners[event.value] = []
        self._listeners[event.value].append(listener)
        self._cur_listeners += 1
        logger.debug(f"{event.value} listener added: {listener.func.__name__}")
        logger.debug(f"Current listeners: {self._cur_listeners}")
        if self._cur_listeners >= self._max_listeners:
            logger.warning("Too many listeners, maybe memory leak!")


from common.const import version

emitter: TypedEventEmitter
if version == "2.0":
    emitter = EventEmitter()
elif version == "2.1":
    emitter = TypedEventEmitter()
