import asyncio
import inspect
import threading
from asyncio import Task
from enum import Enum
from typing import Callable, List, Dict, TypeVar, Coroutine, Any, Tuple
from uuid import uuid4

from loguru import logger

from common.abs_runnable import AbstractRunnable
from common.killable_thread import KillableThread
from event.event_data import BaseEvent

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

    def name(self):
        return "TypedEventEmitter"

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

    async def start(self):
        await super().start()
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
                except RuntimeError as e:
                    # TODO: Here we need to fix it...
                    if "attached to a different loop" in f"{e}":
                        logger.warning(f"Task({task.get_name()}) is attached to a different loop?! Why?!")
                self._tasks.remove(task)
            self._event_pending.clear()
            if self._stop_flag:
                break
            await self._event_pending.wait()

    def _sync_loop(self):
        while not self._stop_flag:
            for listener, event in self._sync_tasks:
                listener.func(event)
                self._sync_tasks.remove((listener, event))

            self._thread_event.clear()
            if self._stop_flag:
                break
            self._thread_event.wait()

    def emit(self, event: Event):
        self.activate_check()
        assert isinstance(event, BaseEvent)
        listeners = self._listeners.get(event.type, None)
        if listeners is None:
            return
        for listener in listeners:
            if listener.once:
                self._listeners[event.type].remove(listener)
            if inspect.iscoroutinefunction(listener.func):
                self._add_async_task(listener, event)
            else:
                self._add_sync_task(listener, event)

    def on(self, event: str):
        assert isinstance(event, str)

        def decorator(func: Callable[[Event], None] | Callable[[Event], Coroutine[Any, Any, None]]):
            assert isinstance(func, Callable)
            self._add_listener(event, Listener(func, False))

        return decorator

    def once(self, event: str):
        assert isinstance(event, str)

        def decorator(func: Callable[[Event], None] | Callable[[Event], Coroutine[Any, Any, None]]):
            assert isinstance(func, Callable)
            self._add_listener(event, Listener(func, True))

        return decorator

    async def stop(self):
        await super().stop()
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

    def _add_listener(self, event: str, listener: Listener):

        listeners = self._listeners.get(event, None)
        if listeners is None:
            self._listeners[event] = []
        self._listeners[event].append(listener)
        self._cur_listeners += 1
        logger.debug(f"{event} listener added: {listener.func.__name__}")
        logger.debug(f"Current listeners: {self._cur_listeners}")
        if self._cur_listeners >= self._max_listeners:
            logger.warning("Too many listeners, maybe memory leak!")


from pymitter import EventEmitter


class NewEventEmitter(EventEmitter):
    def emit(self, *args: Any, **kwargs: Any) -> None:
        event: BaseEvent = args[0]
        super().emit(event.type, event)

    # emitter = TypedEventEmitter()


emitter = NewEventEmitter()
