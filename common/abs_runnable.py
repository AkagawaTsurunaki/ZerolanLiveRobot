import uuid
from abc import abstractmethod
from typing import Dict


class AbstractRunnable:

    def __init__(self):
        self._activate: bool = False
        self._id: str = str(uuid.uuid4())

    @abstractmethod
    async def astart(self):
        self.start()

    @abstractmethod
    def start(self):
        _all[self._id] = self
        self._activate = True

    def activate_check(self):
        if not self._activate:
            raise RuntimeError("This runnable object is not activated. Call `start()` first.")

    @abstractmethod
    async def astop(self):
        self.stop()

    @abstractmethod
    def stop(self):
        assert _all.pop(self._id, None) is not None, f"Some runnable object is ignored? This should not happen!"
        self._activate = False


# 所有的可运行组件都应该在调用 `start` 方法的时候被注册在这里
# All runnable components should be registered here when the `start` method is called
_all: Dict[str, AbstractRunnable] = {}


async def stop_all():
    """
    强制停止所有可运行组件的运行
    Force stop the operation of all runnable components
    """
    global _all
    for id, run in _all.items():
        await run.astop()
