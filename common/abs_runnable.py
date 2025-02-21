import uuid
from abc import abstractmethod
from typing import Dict, List

from loguru import logger


class AbstractRunnable:

    def __init__(self):
        self._activate: bool = False
        self.id: str = str(uuid.uuid4())

    @abstractmethod
    def name(self):
        return self.id

    @abstractmethod
    async def start(self):
        self._activate = True
        add_runnable(self)

    def activate_check(self):
        if not self._activate:
            raise RuntimeError("This runnable object is not activated. Call `start()` first.")

    @abstractmethod
    async def stop(self):
        self._activate = False


class ThreadRunnable:

    def __init__(self):
        self._activate: bool = False
        self.id: str = str(uuid.uuid4())

    @abstractmethod
    def name(self):
        return self.id

    @abstractmethod
    def start(self):
        self._activate = True
        add_runnable(self)

    def activate_check(self):
        if not self._activate:
            raise RuntimeError("This runnable object is not activated. Call `start()` first.")

    @abstractmethod
    def stop(self):
        self._activate = False


# 所有的可运行组件都应该在调用 `start` 方法的时候被注册在这里
# All runnable components should be registered here when the `start` method is called
_all: Dict[str, AbstractRunnable] = {}
_ids: List[str] = []


def add_runnable(run: AbstractRunnable | ThreadRunnable):
    _all[run.id] = run
    _ids.append(run.id)
    logger.debug(f"Runnable {run.name()}: {run.id}")


async def stop_all_runnable():
    """
    强制停止所有可运行组件的运行
    Force stop the operation of all runnable components
    """
    global _all
    ids = _ids.copy()
    ids.reverse()

    for id in ids:
        run = _all.pop(id, None)
        if run is None:
            logger.warning(f"Runnable dose not exist: {id}")
            return
        await run.stop()
        logger.debug(f"Runnable {run.name()}({id}): killed.")
