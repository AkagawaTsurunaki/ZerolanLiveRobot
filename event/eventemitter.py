import asyncio
import inspect
import threading
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


class TypedEventEmitter(AbstractRunnable):

    def name(self):
        return "TypedEventEmitter"

    def __init__(self):
        super().__init__()
        self._max_listeners: int = 100
        self._cur_listeners: int = 0

        # 监听器与待处理（同步和异步）任务
        self._listeners: Dict[str, List[Listener]] = dict()
        # self._coro_queue: Queue[Coroutine[Any, Any, Any]] = Queue()
        self._coro_queue: asyncio.Queue[Coroutine[Any, Any, Any]] = asyncio.Queue()
        self._sync_tasks: List[Tuple[Listener, Event]] = []

        # 线程与信号量
        self._stop_flag: bool = False
        self._async_wait_flag = asyncio.Event()
        self._thread_event = threading.Event()
        self._emitter_thread = KillableThread(target=self._sync_loop, daemon=True,
                                              name="TypedEventEmitterLoop")

    async def start(self):
        await super().start()
        logger.info("Starting...")
        self._stop_flag = False

        # NOTE: Start thread first, then start async event loop.
        self._emitter_thread.start()
        await self._async_loop()

        # Join the thread
        self._emitter_thread.join()

        logger.info("TypedEventEmitter exited")

    async def _async_loop(self):
        loop_counter = 0
        while not self._stop_flag:
            loop_counter += 1
            logger.debug(f"Enter async loop ({loop_counter})")
            logger.debug(f"Count: {self._coro_queue.qsize()}")

            gathered_tasks = []
            while not self._coro_queue.empty():
                # coro = await asyncio.to_thread(self._coro_queue.get)
                coro = await self._coro_queue.get()
                task = asyncio.create_task(coro)
                gathered_tasks.append(task)
            await asyncio.gather(*gathered_tasks)

            logger.debug(f"Tasks done: {[task for task in gathered_tasks]}")

            if self._coro_queue.empty():
                self._async_wait_flag.clear()
                await asyncio.sleep(0)
            await self._async_wait_flag.wait()
            # await asyncio.sleep(1)
            logger.debug(f"Exit async loop ({loop_counter})")

    def _sync_loop(self):
        while not self._stop_flag:
            for listener, event in self._sync_tasks:
                try:
                    listener.func(event)
                except Exception as e:
                    logger.exception(e)
                finally:
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
        self._async_wait_flag.set()
        self._emitter_thread.kill()
        logger.info("Stopping...")

    def _add_sync_task(self, listener: Listener, event: Event):
        self._sync_tasks.append((listener, event))
        self._thread_event.set()
        logger.debug(f"Added sync task to event loop: {listener.func.__name__}")

    def _add_async_task(self, listener: Listener, event: Event):
        coro = listener.func(event)
        assert isinstance(coro, Coroutine)
        # self._coro_queue.put(coro)
        self._coro_queue.put_nowait(coro)
        self._async_wait_flag.set()
        logger.debug(f"_coro_queue size: {self._coro_queue.qsize()}")
        logger.debug(f"Added async task to event loop: {coro.__name__}")

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


emitter = TypedEventEmitter()
