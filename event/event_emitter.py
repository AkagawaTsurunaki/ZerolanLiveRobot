"""
Typed Event Emitter v2
Author: AkagawaTsurunaki

Task:
    When an event is emitted, the tasks will be loaded in real time according to the registered listeners.
    BaseTask has 2 inherited class SyncFunc and AsyncCoro,
    which correspond to a synchronous or asynchronous function that can be called.

Executor:
    AsyncTaskExecutor use event loop to handle AsyncCoros.
    SyncTaskExecutor use thread pool to handle SyncFuncs.

Timeout:
    By default, the timeout duration of a task is 5 seconds,
    and once this event is exceeded, it will be printed on the log.
    The operation will not cancel the task, but only for the diagnosis of the function called.
"""
import asyncio
import inspect
import queue
import threading
import time
import uuid
from abc import abstractmethod
from asyncio import Queue
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Dict, List

from loguru import logger
from typeguard import typechecked

from common.concurrent.killable_thread import KillableThread
from event.event_data import BaseEvent


class Timer:
    def __init__(self, timeout: int, timeout_handler: Callable):
        self._start: int | None = None
        self._end: int | None = None
        self._timeout: int | None = timeout
        if self._timeout:
            self._thread_timer = threading.Timer(self._timeout, timeout_handler)

    def start(self):
        self._start = time.time()
        if self._timeout:
            self._thread_timer.start()

    def stop(self):
        self._end = time.time()
        self._thread_timer.cancel()

    @property
    def elapsed(self):
        if self._start and self._end:
            return self._end - self._start
        if self._start:
            return time.time() - self._end
        raise Exception("Timer has not been started")


class BaseTask:
    def __init__(self, target, name: str = None, timeout: int = None):
        self.id = str(uuid.uuid4())
        assert target is not None, f"Target is null."
        self.name = self.id if name is None else name
        self.target = target
        self._args = None
        self._kwargs = {}
        self.exception = None
        self.timer = Timer(timeout, lambda: logger.warning(f"Task(id={self.id}) {self.name} timeout for {timeout}s!"))

    @abstractmethod
    def execute(self):
        raise NotImplementedError()

    def set_args(self, *args):
        self._args = args

    def set_kwargs(self, **kwargs):
        self._kwargs = kwargs


class SyncFunc(BaseTask):
    def execute(self):
        self.timer.start()
        try:
            self.target(*self._args, **self._kwargs)
        except Exception as e:
            self.exception = e
            logger.exception(e)
            raise e
        finally:
            self.timer.stop()
            logger.debug(f"Function(id={self.id}) {self.name} execution costs {self.timer.elapsed} s")

    def __init__(self, target, name: str = None, timeout: int = None):
        super().__init__(target, name, timeout)


class AsyncCoro(BaseTask):
    async def execute(self):
        self.timer.start()
        try:
            await self.target(*self._args, **self._kwargs)
        except Exception as e:
            self.exception = e
            logger.exception(e)
            raise e
        finally:
            self.timer.stop()
            logger.debug(f"Coroutine(id={self.id}) {self.name} execution costs {self.timer.elapsed} s")

    def __init__(self, target, name: str = None, timeout: int = None):
        super().__init__(target, name, timeout)


class AsyncTaskExecutor:
    def __init__(self):
        self._async_tasks: Queue[AsyncCoro] = Queue()
        # Pending tasks may be deleted by Python-GC,
        # so use strong reference to avoid this issue!
        self._submitted_tasks: List[asyncio.Task] = []

    async def start(self):
        await self._async_event_loop()

    async def stop(self):
        for task in self._submitted_tasks:
            task.cancel()

    async def _async_event_loop(self):
        while True:
            task = await self._async_tasks.get()
            if task:
                t = asyncio.create_task(task.execute())
                self._submitted_tasks.append(t)

    @typechecked
    def add_async_task(self, func: AsyncCoro):
        self._async_tasks.put_nowait(func)


class SyncTaskExecutor:
    def __init__(self, max_workers: int | None = None):
        self._sync_tasks: queue.Queue = queue.Queue()
        self._thread_pool = ThreadPoolExecutor(max_workers=max_workers)

    def start(self):
        self._sync_event_loop()

    def stop(self):
        try:
            self._thread_pool.shutdown(wait=False, cancel_futures=True)
        except Exception as e:
            logger.exception(e)

    def _sync_event_loop(self):
        while True:
            task = self._sync_tasks.get(block=True)
            logger.debug("Get sync task running")
            if task:
                self._thread_pool.submit(task.execute)

    @typechecked
    def add_sync_task(self, func: SyncFunc):
        self._sync_tasks.put_nowait(func)


class Listener:
    def __init__(self, func: Callable, once: bool = False):
        self.func: Callable = func
        self.once: bool = once


class TypedEventEmitter:
    """
    TypedEventEmitter Ver2
    Github@AkagawaTsurunaki
    """
    def __init__(self):
        self._sync_executor = SyncTaskExecutor()
        self._async_executor = AsyncTaskExecutor()
        self.sync_executor_thread: KillableThread | None = None
        self._async_executor_task: asyncio.Task | None = None

        self._listeners: Dict[str, List[Listener]] = dict()

    async def start(self):
        self.sync_executor_thread = KillableThread(target=self._sync_executor.start, daemon=True)
        self._async_executor_task = asyncio.create_task(self._async_executor.start())
        self.sync_executor_thread.start()
        logger.info("TypedEventEmitter is running...")
        await self._async_executor_task
        self.sync_executor_thread.join()

    async def stop(self):
        if self.sync_executor_thread:
            self._sync_executor.stop()
            self.sync_executor_thread.kill()
        if self._async_executor_task:
            await self._async_executor.stop()
            self._async_executor_task.cancel()

    def _add_task(self, func: Callable, event_data: BaseEvent):
        if inspect.iscoroutinefunction(func):
            # Coroutine function
            async_coro = AsyncCoro(target=func, name=func.__name__, timeout=5)
            async_coro.set_args(event_data)
            self._async_executor.add_async_task(async_coro)
        else:
            # Sync function
            sync_func = SyncFunc(target=func, name=func.__name__, timeout=5)
            sync_func.set_args(event_data)
            self._sync_executor.add_sync_task(sync_func)

    def _add_listener(self, event: str, listener: Listener):
        if self._listeners.get(event, None) is None:
            self._listeners[event] = []
        self._listeners[event].append(listener)

    def _create_tasks(self, event: str, event_data: BaseEvent):
        listeners = self._listeners.get(event, None)
        if listeners:
            for listener in listeners:
                if listener.once:
                    listeners.remove(listener)
                self._add_task(listener.func, event_data)

    @typechecked
    def on(self, event: str):
        def decorator(func: Callable):
            self._add_listener(event=event, listener=Listener(func=func, once=False))

        return decorator

    @typechecked
    def once(self, event: str):
        def decorator(func: Callable):
            self._add_listener(event=event, listener=Listener(func=func, once=True))

        return decorator

    @typechecked
    def emit(self, event: BaseEvent):
        self._create_tasks(event.type, event)


emitter = TypedEventEmitter()
