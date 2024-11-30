from abc import abstractmethod


class AbstractRunnable:

    def __init__(self):
        self._activate: bool = False

    @abstractmethod
    async def start(self):
        self._activate = True

    def activate_check(self):
        if not self._activate:
            raise RuntimeError("This runnable object is not activated. Call `start()` first.")

    @abstractmethod
    async def stop(self):
        self._activate = False